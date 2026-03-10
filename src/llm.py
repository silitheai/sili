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
        self.client = ollama.Client(host=host)
        
    def generate(self, prompt: str, system: Optional[str] = None, images: Optional[List[str]] = None) -> str:
        """Sends a prompt to the LLM and returns the text response."""
        model = self.vision_model if images else self.text_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
            
        user_message = {"role": "user", "content": prompt}
        if images:
            user_message["images"] = images
            
        messages.append(user_message)
        
        try:
            # Check availability first to avoid infinite hangs
            if not self.manager.is_model_available(model):
                 return f"Neural Error: Model '{model}' not found in local Ollama storage."

            # Actual generation
            response = self.client.chat(
                model=model,
                messages=messages,
                options={"num_predict": 4096} # Sili Infinity support
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLMWrapper: Generation failed: {e}")
            return f"LLM Generation Error: {str(e)}"
