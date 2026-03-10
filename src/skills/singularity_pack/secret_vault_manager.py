import os
import json

def secret_vault_manager(action: str, key: str = None, value: str = None):
    """Encrypted (simulated) vault for managing Sili's API keys securely."""
    vault_path = os.path.join(os.path.dirname(__file__), "vault.json")
    
    if action == "list":
        if os.path.exists(vault_path):
            with open(vault_path, "r") as f:
                return f"Vault Keys: {', '.join(json.load(f).keys())}"
        return "Vault is empty."
    
    elif action == "set" and key and value:
        vault = {}
        if os.path.exists(vault_path):
            with open(vault_path, "r") as f:
                vault = json.load(f)
        vault[key] = value
        with open(vault_path, "w") as f:
            json.dump(vault, f)
        return f"Key '{key}' secured in Sili's neural vault."
    
    return "Invalid action or missing parameters."
