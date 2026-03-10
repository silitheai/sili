import json
import os
from typing import List, Dict, Any

class MemoryManager:
    """Manages persistent memory storage for OpenClaw using simple JSON."""
    def __init__(self, memory_file_path: str = None):
        if memory_file_path is None:
            # Default to a memory.json in the project root
            memory_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "memory.json"
            )
        self.memory_file = memory_file_path
        self._ensure_memory_file()

    def _ensure_memory_file(self):
        """Creates the memory file if it doesn't exist."""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def get_user_history(self, user_id: str) -> List[Dict[str, str]]:
        """Retrieves the recent conversation history for a specific user ID."""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(str(user_id), [])
        except json.JSONDecodeError:
            return []

    def add_interaction(self, user_id: str, role: str, content: str):
        """Adds a message to the user's persistent memory log."""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

        user_id_str = str(user_id)
        if user_id_str not in data:
            data[user_id_str] = []

        data[user_id_str].append({"role": role, "content": content})
        
        # Keep only the last 20 interactions to prevent context overflow locally
        if len(data[user_id_str]) > 20:
            data[user_id_str] = data[user_id_str][-20:]

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get_context_string(self, user_id: str) -> str:
        """Returns the memory as a formatted context string for the LLM prompt."""
        history = self.get_user_history(user_id)
        if not history:
            return "No previous memory exists."
            
        context = "--- PAST CONVERSATION MEMORY ---\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Agent"
            content = msg["content"]
            # Truncate extremely long past outputs for memory
            if len(content) > 500:
                content = content[:500] + "... [truncated]"
            context += f"{role}: {content}\n"
        return context + "--------------------------------\n"
