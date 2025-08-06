import os
import json
from cryptography.fernet import Fernet, InvalidToken
from agent.config import Config

class VaultManager:
    """
    Manages the secure storage and retrieval of sensitive data (e.g., credit card details)
    using encryption. Data is encrypted/decrypted using a master key.
    """

    def __init__(self):
        self.vault_path = Config.VAULT_PATH
        self.master_key = Config.VAULT_MASTER_KEY
        if not self.master_key:
            raise ValueError("VAULT_MASTER_KEY environment variable is not set. Cannot initialize VaultManager.")
        
        # Ensure the key is base64-encoded for Fernet
        try:
            self.fernet = Fernet(self.master_key.encode("utf-8"))
        except Exception as e:
            raise ValueError(f"Invalid VAULT_MASTER_KEY: {e}. Ensure it's a valid Fernet key.")

        self.vault_data: dict = self._load_vault()

    def _load_vault(self) -> dict:
        """
        Loads and decrypts the vault data from the encrypted file.
        """
        if not os.path.exists(self.vault_path):
            print(f"Vault file not found at {self.vault_path}. Initializing empty vault.")
            return {}
        try:
            with open(self.vault_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_bytes.decode("utf-8"))
        except InvalidToken:
            print("Warning: Could not decrypt vault. Master key might be incorrect or vault is corrupted. Initializing empty vault.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Vault data is not valid JSON after decryption: {e}. Initializing empty vault.")
            return {}
        except Exception as e:
            print(f"Error loading/decrypting vault: {e}. Initializing empty vault.")
            return {}

    def _save_vault(self):
        """
        Encrypts and saves the current vault data to the file.
        """
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        plain_text_bytes = json.dumps(self.vault_data, indent=4).encode("utf-8")
        encrypted_bytes = self.fernet.encrypt(plain_text_bytes)
        with open(self.vault_path, "wb") as f:
            f.write(encrypted_bytes)

    def add_card(self, card_id: str, card_details: dict):
        """
        Adds or updates credit card details in the vault.
        card_details should be a dictionary containing sensitive info (e.g., number, expiry, cvv).
        """
        self.vault_data[card_id] = card_details
        self._save_vault()
        print(f"Card {card_id} added/updated in vault.")

    def get_card_details(self, card_id: str) -> dict | None:
        """
        Retrieves and decrypts credit card details from the vault.
        Returns None if card_id not found.
        """
        details = self.vault_data.get(card_id)
        if details:
            print(f"Card {card_id} details retrieved from vault.")
        else:
            print(f"Card {card_id} not found in vault.")
        return details

    def delete_card(self, card_id: str):
        """
        Deletes credit card details from the vault.
        """
        if card_id in self.vault_data:
            del self.vault_data[card_id]
            self._save_vault()
            print(f"Card {card_id} deleted from vault.")
        else:
            print(f"Card {card_id} not found in vault.")

    def get_all_card_ids(self) -> list[str]:
        """
        Returns a list of all card IDs stored in the vault.
        """
        return list(self.vault_data.keys())




