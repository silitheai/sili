import json
import re
from typing import List, Dict, Any, Optional
from llm import LLMWrapper
from tools.bash import execute_bash
from tools.filesystem import read_file, write_file, list_files
from tools.vision_capture import load_image_as_base64
from tools.browser import brave_web_search
from tools.python_executor import execute_python_code
from memory import MemoryManager
from vector_memory import VectorMemoryManager

class Agent:
    def __init__(self, text_model: str = "llama3.1", vision_model: str = "llama3.2-vision", user_id: str = "default_user"):
        self.llm = LLMWrapper(text_model=text_model, vision_model=vision_model)
        self.system_prompt = self._build_system_prompt()
        self.user_id = user_id
        
        # Dual memory systems
        self.short_memory = MemoryManager()
        self.vector_memory = VectorMemoryManager()
        
        self.max_steps = 15

    def _build_system_prompt(self) -> str:
        return """You are OpenClaw, an exceptionally capable autonomous AI agent running fully locally.
You have access to the following tools to interact with the system and fulfill any request:

1. `bash`: Executes a bash command. Provide the command as a string in the 'command' argument.
2. `read_file`: Reads a file's content. Provide the absolute path in the 'path' argument.
3. `write_file`: Writes content to a file. Provide path and content in 'path' and 'content' arguments.
4. `list_files`: Lists directory contents. Provide the path in the 'path' argument.
5. `web_search`: Searches the web using Brave Search. Provide the query in the 'query' argument.
6. `python_execute`: Executes custom Python code dynamically. You can use this to perform complex tasks, data analysis, or interact with any API (trading, scraping, etc.) by writing a quick script. Provide the complete python script in the 'code' argument. Make sure to print() the output you want to see.
7. `finish`: Call this when you have successfully completed the user's task. Provide a final 'summary'.

IMPORTANT: You must structure your responses strictly in the following format. Do not deviate.

Thought: [Your step-by-step reasoning on what to do next]
Action: [The exact name of the tool you want to use, e.g., bash or python_execute]
Action Input: [A JSON string representing the arguments for the tool. Ensure it is valid JSON.]

Example 1:
Thought: I need to calculate the Fibonacci sequence up to 100. I can write a quick python script for this.
Action: python_execute
Action Input: {"code": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a, end=' ')\n        a, b = b, a+b\n\nfib(10)"}

Example 2:
Thought: I need to search the web for the latest news on AI.
Action: web_search
Action Input: {"query": "latest news artificial intelligence"}

Example 3:
Thought: I have finished the task.
Action: finish
Action Input: {"summary": "I have successfully calculated the sequence."}

Wait for the "Observation:" from the system before taking your next step. Do not hallucinate the observation.
"""

    def _parse_response(self, text: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Parses the LLM response to extract Thought, Action, and Action Input."""
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)(?=\nAction Input:|$)", text)
        input_match = re.search(r"Action Input:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        action_input_raw = input_match.group(1).strip() if input_match else None

        return thought, action, action_input_raw

    def _execute_tool(self, action: str, action_input: Dict[str, Any]) -> str:
        """Executes the mapped tool based on parsed action and input."""
        try:
            if action == 'bash':
                return execute_bash(action_input.get('command', ''))
            elif action == 'read_file':
                return read_file(action_input.get('path', ''))
            elif action == 'write_file':
                return write_file(action_input.get('path', ''), action_input.get('content', ''))
            elif action == 'list_files':
                return list_files(action_input.get('path', ''))
            elif action == 'web_search':
                return brave_web_search(action_input.get('query', ''))
            elif action == 'python_execute':
                return execute_python_code(action_input.get('code', ''))
            elif action == 'finish':
                return action_input.get('summary', 'Task finished without summary.')
            else:
                return f"Error: Tool '{action}' not recognized."
        except Exception as e:
            return f"Error executing tool {action}: {str(e)}"

    def run(self, goal: str, image_paths: Optional[List[str]] = None) -> str:
        """Runs the ReAct agent loop until the goal is met or max steps are reached."""
        print(f"\n[OpenClaw Agent Started] Goal: {goal}")
        
        # Load images if provided
        base64_images = None
        if image_paths:
            base64_images = []
            for path in image_paths:
                try:
                    base64_images.append(load_image_as_base64(path))
                    print(f"Loaded image context from: {path}")
                except Exception as e:
                    print(f"Warning: Failed to load image {path}: {e}")

        # Fetch short term memory and semantic long term memory
        short_term_context = self.short_memory.get_context_string(self.user_id)
        long_term_semantic = self.vector_memory.semantic_search(self.user_id, goal)

        # Construct initial prompt with conversation history context
        prompt = long_term_semantic + "\n" + short_term_context + "\nGoal: " + goal + "\n"
        
        for step in range(self.max_steps):
            print(f"\n--- Step {step+1}/{self.max_steps} ---")
            
            # Use images only on the first turn if available
            current_images = base64_images if step == 0 else None
            
            # Generate next step from LLM
            response_text = self.llm.generate(prompt, self.system_prompt, current_images)
            print(f"\n[LLM Output]\n{response_text}\n")
            
            thought, action, action_input_raw = self._parse_response(response_text)
            
            if not action or not action_input_raw:
                error_msg = "Error: Could not parse Action or Action Input from response. Ensure you are following the exact required format."
                print(error_msg)
                prompt += f"\nObservation: {error_msg}\n"
                continue

            print(f"-> Selected Tool: {action}")
            
            # Try parsing JSON input
            try:
                # Clean up potential markdown formatting around JSON
                cleaned_input = re.sub(r'```json\n|```\n?', '', action_input_raw).strip()
                action_input = json.loads(cleaned_input)
            except json.JSONDecodeError:
                error_msg = f"Error: Invalid JSON in Action Input: {action_input_raw}"
                print(error_msg)
                prompt += f"\n{response_text}\nObservation: {error_msg}\n"
                continue

            if action == 'finish':
                summary = action_input.get('summary', 'Task Finished.')
                print(f"\n[Agent Finished] {summary}")
                
                # Save interaction to both memory systems
                self.short_memory.add_interaction(self.user_id, "user", goal)
                self.short_memory.add_interaction(self.user_id, "agent", summary)
                
                self.vector_memory.add_interaction(self.user_id, "user", goal)
                self.vector_memory.add_interaction(self.user_id, "agent", summary)
                
                return summary

            # Execute tool
            observation = self._execute_tool(action, action_input)
            
            # Truncate observation if too long for local context windows
            if len(observation) > 4000:
                observation = observation[:4000] + "... [TRUNCATED]"
                
            print(f"\n[Observation]\n{observation}")
            
            # Append context for next iteration
            prompt += f"\n{response_text}\nObservation: {observation}\n"

        failure_msg = "Agent stopped: Reached maximum number of steps without finishing."
        print(f"\n[Agent Stopped] {failure_msg}")
        return failure_msg
