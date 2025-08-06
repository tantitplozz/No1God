import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

import dspy
from dspy.teleprompt import LabeledFewShot

from agent.config import Config
from agent.brain.knowledge_base import KnowledgeBase
from agent.brain.vault_manager import VaultManager
from agent.core.agent_runtime import AgentRuntime
from agent.brain.strategy_library.warmup_turbo import WarmupTurboStrategy
from agent.brain.strategy_library.surgical_strike import SurgicalStrikeStrategy
from agent.core.dspy_signatures import PlanMission, SelectToolAndArguments, AnalyzeFailure, ExtractInfo

class Orchestrator:
    """
    The brain of the Chimera Overlord. It orchestrates missions, manages agent state,
    interacts with the knowledge base, vault, and agent runtime, and uses DSPy for decision-making.
    """

    def __init__(self):
        self.kb = KnowledgeBase()
        self.vault = VaultManager()
        self.runtime: Optional[AgentRuntime] = None
        self.dspy_lm = dspy.OpenAI(model=\


"gpt-4o", api_key=Config.OPENAI_API_KEY, api_base=Config.OPENAI_API_BASE)
        dspy.settings.configure(lm=self.dspy_lm)

        # DSPy Modules
        self.plan_mission_module = dspy.ChainOfThought(PlanMission)
        self.select_tool_module = dspy.ChainOfThought(SelectToolAndArguments)
        self.analyze_failure_module = dspy.ChainOfThought(AnalyzeFailure)
        self.extract_info_module = dspy.ChainOfThought(ExtractInfo)

    async def _execute_dspy_step(self, signature_module, **kwargs):
        """
        Helper to execute DSPy modules and handle potential errors.
        """
        try:
            return await signature_module(**kwargs)
        except Exception as e:
            print(f"DSPy execution failed for {signature_module.__class__.__name__}: {e}")
            return None

    async def run_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point to run a mission.
        """
        mission_id = mission_data.get("mission_id", f"mission_{datetime.now().strftime("%Y%m%d%H%M%S")}")
        profile_name = mission_data.get("profile_name", "default_profile")
        target_website = mission_data.get("target_website")
        product_identifier = mission_data.get("product_identifier")
        force_warmup = mission_data.get("force_warmup", False)
        trust_score_threshold = mission_data.get("trust_score_threshold", Config.DEFAULT_TRUST_SCORE_THRESHOLD)
        primary_card_id = mission_data.get("primary_card_id")
        secondary_card_id = mission_data.get("secondary_card_id")

        print(f"Starting mission: {mission_id} for {target_website} - {product_identifier}")

        # Initialize runtime
        self.runtime = AgentRuntime(mission_id, profile_name)
        await self.runtime.initialize()

        # Load card details securely
        primary_card_details = None
        if primary_card_id:
            primary_card_details = self.vault.get_card_details(primary_card_id)
        secondary_card_details = None
        if secondary_card_id:
            secondary_card_details = self.vault.get_card_details(secondary_card_id)

        mission_data["primary_card"] = primary_card_details
        mission_data["secondary_card"] = secondary_card_details

        # --- Stateful Recovery Check ---
        last_mission_state = self.kb.get_mission_state(mission_id)
        if last_mission_state and last_mission_state.get("status") == "in_progress":
            print(f"Resuming mission {mission_id} from last known state.")
            # Implement logic to resume from a specific step based on last_mission_state
            # For now, we'll just re-run the main strategy.

        # --- Warmup Phase ---
        current_trust_score = self.kb.get_profile_trust_score(profile_name)
        print(f"Current Trust Score for {profile_name}: {current_trust_score}")

        if force_warmup or current_trust_score < trust_score_threshold:
            print("Initiating Warmup Turbo strategy...")
            warmup_strategy = WarmupTurboStrategy(self.runtime, mission_data)
            warmup_result = await warmup_strategy.execute()
            if warmup_result["status"] == "success":
                new_trust_score = current_trust_score + warmup_result.get("trust_score_increase", 0)
                self.kb.update_profile_trust_score(profile_name, new_trust_score)
                print(f"Warmup successful. New Trust Score: {new_trust_score}")
            else:
                print(f"Warmup failed: {warmup_result.get("message")}")
                # Decide if mission should proceed without sufficient warmup
                # For now, we proceed, but this could be a failure point.

        # --- Main Mission Execution (Surgical Strike) ---
        print("Initiating Surgical Strike strategy...")
        surgical_strike_strategy = SurgicalStrikeStrategy(self.runtime, mission_data)
        mission_result = await surgical_strike_strategy.execute()

        # --- Post-mission Actions ---
        await self.runtime.close()

        # Update mission history
        final_status = mission_result.get("status", "failed")
        final_outcome = mission_result.get("outcome", "unknown")
        final_message = mission_result.get("message", "No specific message.")

        mission_record = {
            "mission_id": mission_id,
            "profile_name": profile_name,
            "target_website": target_website,
            "product_identifier": product_identifier,
            "start_time": mission_data.get("start_time", datetime.now().isoformat()),
            "end_time": datetime.now().isoformat(),
            "status": final_status,
            "outcome": final_outcome,
            "message": final_message,
            "final_trust_score": self.kb.get_profile_trust_score(profile_name),
            "trace_file": self.runtime.trace_path if final_status == "failed" else None # Only save trace for failed missions by default
        }
        self.kb.add_mission_history(mission_record)

        print(f"Mission {mission_id} finished with status: {final_status}, outcome: {final_outcome}")
        return mission_record

    def add_new_card(self, card_details: Dict[str, Any]) -> str:
        """
        Adds new card details to the vault and returns a unique card ID.
        """
        card_id = f"card_{datetime.now().strftime("%Y%m%d%H%M%S")}_{os.urandom(4).hex()}"
        self.vault.add_card(card_id, card_details)
        self.kb.add_card_vault_reference(
            card_id,
            encrypted_vault_entry_id=card_id, # In this simple setup, card_id is the entry ID
            last4=card_details.get("number", "")[-4:],
            card_type=card_details.get("type", "Unknown")
        )
        return card_id

    def get_available_cards(self) -> Dict[str, Any]:
        """
        Returns a dictionary of available card references (not actual details).
        """
        return self.kb.get_all_card_vault_references()

    def get_mission_history(self) -> list[Dict[str, Any]]:
        """
        Returns the full mission history.
        """
        return self.kb.get_mission_history()

    def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Returns information about a specific profile.
        """
        return {
            "name": profile_name,
            "trust_score": self.kb.get_profile_trust_score(profile_name)
        }




