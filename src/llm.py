import os
import ollama
import logging
from typing import List, Dict, Any, Optional
from src.brain.ollama_manager import OllamaManager

logger = logging.getLogger(__name__)

class LLMWrapper:
    def __init__(self, text_model: str = None, vision_model: str = None, host: str = "http://localhost:11434"):
        """Initializes the LLM wrapper connecting to a local Ollama instance."""
        self.text_model = text_model or os.getenv("TEXT_MODEL", "llama3.1")
        self.vision_model = vision_model or os.getenv("VISION_MODEL", "llama3.2-vision")
        self.manager = OllamaManager(host=host)
        self.client = ollama.AsyncClient(host=host) # V16.9 Async Singularity
        
    async def generate(self, prompt: str, system: Optional[str] = None, images: Optional[List[str]] = None, timeout: float = 60.0) -> str:
        """Sends a prompt to the LLM and returns the text response (Async)."""
        model = self.vision_model if images else self.text_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
            
        user_message = {"role": "user", "content": prompt}
        if images:
            user_message["images"] = images
            
        messages.append(user_message)
        
        try:
            # Check availability first (Now correctly awaited)
            if not await self.manager.is_model_available(model):
                 return f"Neural Error: Model '{model}' not found in local Ollama storage."

            # Actual generation (Async with strict timeout)
            # V16.10: Using wait_for to prevent infinite Ollama hangs
            response = await asyncio.wait_for(
                self.client.chat(
                    model=model,
                    messages=messages,
                    options={"num_predict": 4096}
                ),
                timeout=timeout
            )
            return response['message']['content']
        except asyncio.TimeoutError:
            logger.error(f"LLMWrapper: Generation timed out after {timeout}s")
            return f"Neural Error: Generation timed out after {timeout}s. Your local model might be too slow or stuck."
        except Exception as e:
            logger.error(f"LLMWrapper: Generation failed: {e}")
            return f"LLM Generation Error: {str(e)}"
