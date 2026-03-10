import ollama
from typing import List, Dict, Any, Optional

class LLMWrapper:
    def __init__(self, text_model: str = "llama3.1", vision_model: str = "llama3.2-vision", host: str = "http://localhost:11434"):
        """Initializes the LLM wrapper connecting to a local Ollama instance.
        
        Args:
            text_model: The name of the model to use for standard text reasoning.
            vision_model: The name of the model to use for vision tasks.
            host: The URL of the Ollama host (default is localhost).
        """
        self.text_model = text_model
        self.vision_model = vision_model
        self.client = ollama.Client(host=host)
        
    def generate(self, prompt: str, system: Optional[str] = None, images: Optional[List[str]] = None) -> str:
        """Sends a prompt to the LLM and returns the text response.
        Automatically uses the vision model if images are provided.
        
        Args:
            prompt: The user query or task.
            system: Optional system prompt to guide the model behavior.
            images: Optional list of base64 encoded image strings.
        """
        model = self.vision_model if images else self.text_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
            
        user_message = {"role": "user", "content": prompt}
        if images:
            user_message["images"] = images
            
        messages.append(user_message)
        
        try:
            response = self.client.chat(
                model=model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"LLM Generation Error: {str(e)}"
