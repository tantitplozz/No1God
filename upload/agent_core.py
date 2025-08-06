# ghost_cell/src/agent_core.py

import os
import json
import dspy
from playwright.sync_api import sync_playwright, Page, Browser
import requests
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .anti_detection import StealthArmor
from .memory_system import MemorySystem
from .dspy_signatures import GeneratePlan, AnalyzeContentAndRefinePlan

class AgentState(TypedDict):
    task: str
    plan: List[str]
    page_content: str
    scratchpad: List[str]
    browser_session: dict
    final_answer: str

class ChimeraAgentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_plan = dspy.Predict(GeneratePlan)
        self.refine_plan = dspy.Predict(AnalyzeContentAndRefinePlan)

    def forward(self, task, page_content, scratchpad, plan):
        pass

class AgentCore:
    def __init__(self, guardian):
        self.guardian = guardian
        self.cell_id = guardian.cell_id
        self.memory = MemorySystem(self.cell_id)
        self.morelogin_base_url = os.getenv("MORELOGIN_API_BASE_URL")
        
        # DSPy Setup
        self.turbo = dspy.OpenAI(
            model='meta-llama/llama-3-8b-instruct',
            api_base="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=2000
        )
        dspy.settings.configure(lm=self.turbo)
        
        self.agent_module = ChimeraAgentModule()
        
        self.tools = {
            "NAVIGATE": {
                "action": self._tool_node_navigate,
                "description": "Navigates the browser to a specified URL. Usage: NAVIGATE to URL: [URL]"
            },
            "TYPE": {
                "action": self._tool_node_type,
                "description": "Types text into an element specified by a CSS selector. Usage: TYPE 'text to type' into 'CSS selector'"
            },
            "CLICK": {
                "action": self._tool_node_click,
                "description": "Clicks on an element specified by a CSS selector. Usage: CLICK on 'CSS selector'"
            },
            "SCRAPE": {
                "action": self._tool_node_scrape,
                "description": "Scrapes the full HTML content of the current page for analysis."
            },
            "FINISH": {
                "action": self._finish_node,
                "description": "Finishes the task and provides the final answer. Usage: FINISH with 'your final answer'"
            }
        }
        self.graph = self._build_graph()
        print(f"AgentCore for Cell [{self.cell_id}] initialized with Weaponized DSPy brain.")

    def _tool_node_navigate(self, state: AgentState):
        print("--- TOOL: Navigating ---")
        page = state["browser_session"]["page"]
        stealth = state["browser_session"]["stealth"]
        
        try:
            # Extract URL from the last action
            last_action = state["scratchpad"][-1]
            if "URL:" in last_action:
                url = last_action.split("URL:")[1].strip()
            else:
                url = "https://www.google.com"
            
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            stealth.human_like_wait(3, 6)
            stealth.handle_cookie_banner()
            
            content = page.content()
            state["page_content"] = content
            state["scratchpad"].append(f"OK. Successfully navigated to {url}.")
        except Exception as e:
            state["scratchpad"].append(f"ERROR. Failed to navigate. Error: {e}")
            
        return state

    def _tool_node_type(self, state: AgentState):
        print("--- TOOL: Typing ---")
        stealth = state["browser_session"]["stealth"]
        page = state["browser_session"]["page"]
        
        try:
            last_action = state["scratchpad"][-1]
            parts = last_action.split("'")
            if len(parts) >= 4:
                text_to_type = parts[1]
                selector = parts[3]
                
                target_locator = page.locator(selector)
                stealth.slow_human_typing(target_locator, text_to_type)
                state["scratchpad"].append(f"OK. Typed '{text_to_type}' into '{selector}'.")
            else:
                state["scratchpad"].append("ERROR. Failed to parse TYPE command.")
        except Exception as e:
            state["scratchpad"].append(f"ERROR. Failed to execute typing. Error: {e}")
            
        return state

    def _tool_node_click(self, state: AgentState):
        print("--- TOOL: Clicking ---")
        stealth = state["browser_session"]["stealth"]
        page = state["browser_session"]["page"]
        
        try:
            last_action = state["scratchpad"][-1]
            parts = last_action.split("'")
            if len(parts) >= 2:
                selector = parts[1]
                target_locator = page.locator(selector)
                stealth.natural_click(target_locator)
                state["scratchpad"].append(f"OK. Clicked on '{selector}'.")
            else:
                state["scratchpad"].append("ERROR. Failed to parse CLICK command.")
        except Exception as e:
            state["scratchpad"].append(f"ERROR. Failed to execute click. Error: {e}")
            
        return state

    def _tool_node_scrape(self, state: AgentState):
        print("--- TOOL: Scraping Page ---")
        page = state["browser_session"]["page"]
        try:
            content = page.content()
            state["page_content"] = content
            state["scratchpad"].append("OK. Successfully re-scraped the page content.")
        except Exception as e:
            state["scratchpad"].append(f"ERROR. Failed to scrape the page. Error: {e}")
        return state

    def _finish_node(self, state: AgentState):
        print("--- FINISHING ---")
        state["final_answer"] = "Task finished. Final summary: " + " | ".join(state["scratchpad"])
        return state

    def _planner_node(self, state: AgentState):
        print("--- DSPy AI: Generating Initial Plan ---")
        
        tool_descriptions = {name: data["description"] for name, data in self.tools.items()}
        
        prediction = self.agent_module.generate_plan(
            task=state["task"],
            allowed_tools=json.dumps(tool_descriptions, indent=2)
        )
        try:
            plan_json = prediction.plan.replace("```json\n", "").replace("```", "")
            state["plan"] = json.loads(plan_json)
        except Exception as e:
            print(f"DSPy Plan Parsing Error: {e}. Falling back to a simple plan.")
            state["plan"] = [f"NAVIGATE to URL: https://google.com/search?q={state['task']}", "FINISH with 'Could not generate a plan.'"]
            
        state["scratchpad"].append(f"Initial plan: {state['plan']}")
        return state

    def _router_node(self, state: AgentState):
        if not state["plan"]:
            return "FINISH"
        
        next_action_str = state["plan"].pop(0)
        state["scratchpad"].append(f"Executing: {next_action_str}")
        
        command = next_action_str.split(" ")[0].upper()
        
        if command in self.tools:
            return command
        else:
            print(f"Unknown command: '{command}'. Finishing.")
            return "FINISH"

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)
        
        for name, data in self.tools.items():
            graph_builder.add_node(name, data["action"])
            
        graph_builder.add_node("planner", self._planner_node)
        
        graph_builder.set_entry_point("planner")
        
        graph_builder.add_conditional_edges(
            "planner",
            self._router_node,
            {tool_name: tool_name for tool_name in self.tools.keys()}
        )
        
        for tool_name in self.tools.keys():
            if tool_name != "FINISH":
                graph_builder.add_conditional_edges(
                    tool_name,
                    self._router_node,
                    {name: name for name in self.tools.keys()}
                )
        
        graph_builder.add_edge("FINISH", END)
        return graph_builder.compile(checkpointer=MemorySaver())

    def _start_browser(self) -> dict:
        profile_id = self.guardian.ledger.get("morelogin_profile_id")
        if not profile_id:
            raise Exception("MoreLogin Profile ID not found in ledger.")

        start_url = f"{self.morelogin_base_url}/api/v2/browser/start?profileId={profile_id}"
        print(f"▶️ AgentCore: Requesting to start browser for profile {profile_id}...")
        resp = requests.get(start_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"MoreLogin API Error: {data.get('msg')}")

        ws_url = data["data"]["ws"]
        print(f"✅ AgentCore: Received WebSocket URL. Connecting...")
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(ws_url, timeout=60000)
        context = browser.contexts[0]
        page = context.pages[0]
        page.set_default_timeout(45000)
        stealth = StealthArmor(page)
        
        print(f"✅ AgentCore: Browser connected for Cell [{self.cell_id}].")
        return {"playwright": playwright, "browser": browser, "page": page, "stealth": stealth}

    def _stop_browser(self, browser_session: dict):
        if browser_session["browser"]:
            try:
                browser_session["browser"].close()
            except Exception as e:
                print(f"⚠️ AgentCore: Error closing browser: {e}")
        if browser_session["playwright"]:
            browser_session["playwright"].stop()
        print(f"🔒 AgentCore: Browser session stopped for Cell [{self.cell_id}].")

    def execute_task(self, task_prompt: str):
        print(f"\n🚀 AgentCore [{self.cell_id}] starting AI task: '{task_prompt}'")
        browser_session = None
        try:
            browser_session = self._start_browser()
            
            initial_state = {
                "task": task_prompt,
                "plan": [],
                "page_content": "",
                "scratchpad": [],
                "browser_session": browser_session,
                "final_answer": ""
            }
            
            config = {"configurable": {"thread_id": f"cell-thread-{self.cell_id}"}}
            final_state = self.graph.invoke(initial_state, config=config)
            
            result = {"status": "success", "message": final_state.get("final_answer", "No final answer.")}
            self.memory.add_memory(
                text=f"AI task '{task_prompt}' completed. Result: {result['message']}",
                metadata={"task_prompt": task_prompt}
            )

        except Exception as e:
            print(f"❌ AgentCore: An error occurred during AI task execution: {e}")
            result = {"error": str(e)}
        
        finally:
            if browser_session:
                self._stop_browser(browser_session)

        print(f"✅ AgentCore [{self.cell_id}] finished AI task.")
        return result

