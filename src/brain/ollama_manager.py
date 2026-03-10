import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaManager:
    """
    Centralized manager for Ollama telemetry and model discovery.
    Ensures Sili is always in sync with the local Ollama instance.
    """
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.api_tags = f"{host}/api/tags"
        self.api_show = f"{host}/api/show"
        
    def get_available_models(self) -> List[str]:
        """Fetches all downloaded models from Ollama."""
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"OllamaManager: Failed to fetch models: {e}")
            return []

    def is_model_available(self, model_name: str) -> bool:
        """Checks if a specific model is downloaded."""
        models = self.get_available_models()
        return model_name in models or f"{model_name}:latest" in models

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Fetches detailed info about a model (parameters, template, etc.)."""
        try:
            response = requests.post(self.api_show, json={"name": model_name}, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"OllamaManager: Failed to fetch info for {model_name}: {e}")
            return {}

    def verify_connectivity(self, model_name: str) -> bool:
        """Runs a tiny test prompt to ensure the model is responsive."""
        try:
            api_generate = f"{self.host}/api/generate"
            payload = {
                "model": model_name,
                "prompt": "hi",
                "stream": False,
                "options": {"num_predict": 1}
            }
            # 10 second timeout for the test prompt
            response = requests.post(api_generate, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OllamaManager: Selection test failed for {model_name}: {e}")
            return False

    def get_status_summary(self) -> str:
        """Returns a string summary of the Ollama state."""
        models = self.get_available_models()
        if not models:
            return "Ollama check: Offline or No Models."
        return f"Ollama check: Online ({len(models)} models available)."
