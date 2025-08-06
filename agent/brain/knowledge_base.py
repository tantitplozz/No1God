import json
import os
from typing import Dict, Any, List
from agent.config import Config

class KnowledgeBase:
    """
    Manages the persistent storage and retrieval of agent knowledge,
    including trust scores, mission history, and references to card vault entries.
    """

    def __init__(self):
        self.kb_path = Config.KNOWLEDGE_BASE_PATH
        self.data: Dict[str, Any] = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Loads the knowledge base from the JSON file.
        Initializes with default structure if file does not exist.
        """
        if not os.path.exists(self.kb_path):
            print(f"Knowledge base file not found at {self.kb_path}. Initializing new one.")
            return {
                "profiles": {},
                "mission_history": [],
                "card_vault_references": {}
            }
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding knowledge base JSON: {e}. Initializing new one.")
            return {
                "profiles": {},
                "mission_history": [],
                "card_vault_references": {}
            }
        except Exception as e:
            print(f"Error loading knowledge base: {e}. Initializing new one.")
            return {
                "profiles": {},
                "mission_history": [],
                "card_vault_references": {}
            }

    def _save_knowledge_base(self):
        """
        Saves the current state of the knowledge base to the JSON file.
        """
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def get_profile_trust_score(self, profile_name: str) -> float:
        """
        Retrieves the trust score for a given profile.
        Returns 50.0 if the profile does not exist.
        """
        return self.data["profiles"].get(profile_name, {"trust_score": 50.0})["trust_score"]

    def update_profile_trust_score(self, profile_name: str, new_score: float):
        """
        Updates the trust score for a given profile.
        """
        if profile_name not in self.data["profiles"]:
            self.data["profiles"][profile_name] = {}
        self.data["profiles"][profile_name]["trust_score"] = max(0.0, min(100.0, new_score)) # Keep score between 0 and 100
        self._save_knowledge_base()

    def add_mission_history(self, mission_record: Dict[str, Any]):
        """
        Adds a new mission record to the history.
        """
        self.data["mission_history"].append(mission_record)
        self._save_knowledge_base()

    def get_mission_history(self) -> List[Dict[str, Any]]:
        """
        Returns the entire mission history.
        """
        return self.data["mission_history"]

    def add_card_vault_reference(self, card_id: str, encrypted_vault_entry_id: str, last4: str, card_type: str):
        """
        Adds a reference to an encrypted card entry in the vault.
        """
        self.data["card_vault_references"][card_id] = {
            "encrypted_vault_entry_id": encrypted_vault_entry_id,
            "last4": last4,
            "card_type": card_type
        }
        self._save_knowledge_base()

    def get_card_vault_reference(self, card_id: str) -> Dict[str, Any] | None:
        """
        Retrieves a reference to an encrypted card entry.
        """
        return self.data["card_vault_references"].get(card_id)

    def get_all_card_vault_references(self) -> Dict[str, Any]:
        """
        Returns all stored card vault references.
        """
        return self.data["card_vault_references"]

    def update_mission_status(self, mission_id: str, status: str, outcome: str, message: str = ""):
        """
        Updates the status of a specific mission in the history.
        This is useful for stateful recovery.
        """
        for record in self.data["mission_history"]:
            if record.get("mission_id") == mission_id:
                record["status"] = status
                record["outcome"] = outcome
                record["message"] = message
                record["last_updated"] = datetime.now().isoformat()
                self._save_knowledge_base()
                return
        print(f"Warning: Mission {mission_id} not found in history for status update.")

    def get_mission_state(self, mission_id: str) -> Dict[str, Any] | None:
        """
        Retrieves the last saved state for a given mission, for recovery purposes.
        """
        # This would be more complex in a real stateful recovery system,
        # potentially storing more granular checkpoints within the mission record.
        for record in self.data["mission_history"]:
            if record.get("mission_id") == mission_id:
                return record
        return None




