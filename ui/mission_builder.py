from typing import Dict, Any, List
from agent.brain.orchestrator import Orchestrator

class MissionBuilder:
    """
    Helps construct mission requests and interact with the Orchestrator
    for managing cards and retrieving mission history.
    """

    def __init__(self):
        self.orchestrator = Orchestrator()

    def build_mission_request(self,
                              target_website: str,
                              product_identifier: str,
                              primary_card_id: str,
                              secondary_card_id: str = None,
                              profile_name: str = "default_profile",
                              force_warmup: bool = False) -> Dict[str, Any]:
        """
        Constructs a dictionary representing a mission request.
        """
        mission_request = {
            "target_website": target_website,
            "product_identifier": product_identifier,
            "primary_card_id": primary_card_id,
            "profile_name": profile_name,
            "force_warmup": force_warmup
        }
        if secondary_card_id:
            mission_request["secondary_card_id"] = secondary_card_id
        
        return mission_request

    def add_new_card(self, card_details: Dict[str, Any]) -> str:
        """
        Adds new card details to the vault via the Orchestrator.
        Returns the unique card ID.
        """
        return self.orchestrator.add_new_card(card_details)

    def get_available_cards(self) -> Dict[str, Any]:
        """
        Retrieves available card references from the Orchestrator.
        """
        return self.orchestrator.get_available_cards()

    def get_mission_history(self) -> List[Dict[str, Any]]:
        """
        Retrieves the full mission history from the Orchestrator.
        """
        return self.orchestrator.get_mission_history()

    def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Retrieves profile information (e.g., trust score) from the Orchestrator.
        """
        return self.orchestrator.get_profile_info(profile_name)




