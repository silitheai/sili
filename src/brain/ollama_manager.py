import httpx
import json
import logging
import os
import asyncio
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaManager:
    """
    Centralized manager for Ollama telemetry and model discovery.
    Ensures Sili is always in sync with the local Ollama instance.
    Uses Asyncio-friendly httpx.
    """
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.api_tags = f"{host}/api/tags"
        self.api_show = f"{host}/api/show"
        
    async def get_available_models(self) -> List[str]:
        """Fetches all downloaded models from Ollama (Async)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_tags, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [m['name'] for m in data.get("models", [])]
                return []
        except Exception as e:
            logger.error(f"OllamaManager: Failed to fetch models: {e}")
            return []

    async def list_local_models(self) -> List[str]:
        """Alias for get_available_models to maintain compatibility (Async)."""
        return await self.get_available_models()

    async def is_model_available(self, model_name: str) -> bool:
        """Checks if a specific model is downloaded (Async)."""
        models = await self.get_available_models()
        return model_name in models or f"{model_name}:latest" in models

    async def verify_connectivity(self, model_name: str) -> bool:
        """Runs a tiny test prompt to ensure the model is responsive (Async)."""
        try:
            api_generate = f"{self.host}/api/generate"
            payload = {
                "model": model_name,
                "prompt": "hi",
                "stream": False,
                "options": {"num_predict": 1}
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(api_generate, json=payload, timeout=10.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OllamaManager: Connectivity test failed for {model_name}: {e}")
            return False

    def get_status_summary_sync(self) -> str:
        """Fallback sync summary for terminal heartbeat."""
        import requests
        try:
            response = requests.get(self.api_tags, timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return f"Ollama check: Online ({len(models)} models available)."
            return "Ollama check: Service Unreachable."
        except:
            return "Ollama check: Offline."

    async def get_status_summary(self) -> str:
        """Returns an async string summary of the Ollama state."""
        models = await self.get_available_models()
        if not models:
            return "Ollama check: Offline or No Models."
        return f"Ollama check: Online ({len(models)} models available)."
