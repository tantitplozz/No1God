import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext

from agent.core.toolset_dom import ToolsetDOM
from agent.core.toolset_vision import ToolsetVision
from agent.core.stealth_armor import StealthArmor

class AgentRuntime:
    """
    Manages the Playwright browser context, orchestrates tool execution (DOM/Vision),
    and handles session tracing for debugging.
    """

    def __init__(self, mission_id: str, profile_name: str = "default_profile"):
        self.mission_id = mission_id
        self.profile_name = profile_name
        self.browser = None
        self.context = None
        self.page = None
        self.dom_tools = None
        self.vision_tools = None
        self.stealth_armor = None
        self.trace_path = os.path.join("data", "traces", f"{self.mission_id}_trace.zip")
        self.user_data_dir = os.path.join("data", "profiles", self.profile_name)
        os.makedirs(self.user_data_dir, exist_ok=True)

    async def initialize(self):
        """
        Initializes the Playwright browser, context, and toolsets.
        """
        print(f"Initializing agent runtime for mission {self.mission_id}...")
        self.browser = await async_playwright().chromium.launch(headless=True) # Set to False for visual debugging
        
        # Use persistent context for profile management
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={
                "width": 1920,
                "height": 1080
            },
            locale="en-US",
            timezone_id="America/New_York",
            accept_downloads=True,
            ignore_https_errors=True,
            # For persistent context, use launch_persistent_context instead of new_context
            # self.context = await async_playwright().chromium.launch_persistent_context(
            #     self.user_data_dir,
            #     headless=True,
            #     viewport={"width": 1920, "height": 1080}
            # )
        )

        # Start tracing
        await self.context.tracing.start(screenshots=True, snapshots=True, sources=True)

        self.page = await self.context.new_page()
        self.stealth_armor = StealthArmor(self.page)
        self.dom_tools = ToolsetDOM(self.page, self.stealth_armor)
        self.vision_tools = ToolsetVision(self.page)
        
        # Apply initial stealth measures
        await self.stealth_armor.apply_stealth()
        print("Agent runtime initialized.")

    async def execute_tool(self, tool_name: str, tool_args: dict) -> dict:
        """
        Executes a specified tool (DOM or Vision) with given arguments.
        Returns a dictionary with success status and any relevant output.
        """
        print(f"Executing tool: {tool_name} with args: {tool_args}")
        result = {"success": False, "output": None, "error": None}

        try:
            if hasattr(self.dom_tools, tool_name):
                method = getattr(self.dom_tools, tool_name)
                result["output"] = await method(**tool_args)
                result["success"] = True
            elif hasattr(self.vision_tools, tool_name):
                method = getattr(self.vision_tools, tool_name)
                result["output"] = await method(**tool_args)
                result["success"] = True
            else:
                result["error"] = f"Tool \'{tool_name}\' not found."
        except Exception as e:
            result["error"] = str(e)
            print(f"Error executing tool {tool_name}: {e}")

        return result

    async def get_current_page_info(self) -> dict:
        """
        Returns the current page's URL and HTML content.
        """
        try:
            html = await self.page.content()
            url = self.page.url
            return {"url": url, "html": html}
        except Exception as e:
            print(f"Error getting current page info: {e}")
            return {"url": "", "html": ""}

    async def close(self):
        """
        Closes the browser and saves the trace.
        """
        if self.context:
            await self.context.tracing.stop(path=self.trace_path)
            print(f"Session trace saved to: {self.trace_path}")
            await self.context.close()
        if self.browser:
            await self.browser.close()
        print("Agent runtime closed.")

# Example Usage (for testing purposes)
async def main():
    mission_id = f"test_mission_{datetime.now().strftime("%Y%m%d%H%M%S")}"
    runtime = AgentRuntime(mission_id)
    try:
        await runtime.initialize()
        
        # Example: Navigate to a page
        nav_result = await runtime.execute_tool("navigate", {"url": "https://www.google.com"})
        print(f"Navigation result: {nav_result}")
        
        # Example: Type into search box
        if nav_result["success"]:
            page_info = await runtime.get_current_page_info()
            print(f"Current URL: {page_info["url"]}")
            # You would typically use DSPy to get the selector, but for example, we'll hardcode
            type_result = await runtime.execute_tool("type_text", {"selector": "textarea[name=\"q\"]", "text": "Playwright Python"})
            print(f"Type result: {type_result}")
            
            # Example: Click search button
            if type_result["success"]:
                click_result = await runtime.execute_tool("click_element", {"selector": "input[name=\"btnK\"]"})
                print(f"Click result: {click_result}")
                
                # Example: Take screenshot
                await runtime.dom_tools.take_screenshot(f"logs/{mission_id}_search_results.png")

    except Exception as e:
        print(f"An error occurred during runtime example: {e}")
    finally:
        await runtime.close()

if __name__ == "__main__":
    asyncio.run(main())


