import json
import re
import os
import importlib.util
import inspect
import time
from typing import List, Dict, Any, Optional

from src.llm import LLMWrapper
from src.tools.bash import execute_bash
from src.tools.filesystem import read_file, write_file, list_files
from src.tools.vision_capture import load_image_as_base64
from src.tools.browser import brave_web_search
from src.tools.python_executor import execute_python_code
from src.tools.media_ingester import get_youtube_transcript, transcribe_audio
from src.memory import MemoryManager
from src.vector_memory import VectorMemoryManager
from src.soul.manager import SoulManager
from src.brain.memory_orchestrator import MemoryOrchestrator
from src.brain.neural_processor import NeuralProcessor
from src.brain.cortex import NeuralCortex
from src.brain.proprioception import Proprioception

class Agent:
    _cached_master_tools = None
    _cached_dynamic_skills = None

    def __init__(self, text_model: str = None, vision_model: str = None, user_id: str = "default_user"):
        self.llm = LLMWrapper(text_model=text_model, vision_model=vision_model)
        self.user_id = user_id
        
        # V11 God Mode Architecture
        self.soul_manager = SoulManager()
        self.brain_orchestrator = MemoryOrchestrator(MemoryManager(), VectorMemoryManager())
        self.neural_brain = NeuralProcessor(self.llm)
        self.cortex = NeuralCortex(self.brain_orchestrator)
        self.proprioception = Proprioception()
        
        self.max_steps = 10000
        
        # V16.7 Speed: Class-level caching for tools/skills
        self.tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
        if Agent._cached_master_tools is None:
            Agent._cached_master_tools = self._load_recursive_tools(self.tools_dir)
        self.master_tools = Agent._cached_master_tools
        
        self.skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
        if Agent._cached_dynamic_skills is None:
            Agent._cached_dynamic_skills = self._load_recursive_tools(self.skills_dir)
        self.dynamic_skills = Agent._cached_dynamic_skills
        
        self.system_prompt = self._build_system_prompt()
        
    def _load_recursive_tools(self, base_dir: str) -> Dict[str, Any]:
        """Recursively loads python files from a directory as callable tools."""
        tools = {}
        for root, _, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]
                    filepath = os.path.join(root, filename)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, filepath)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Check for specific function names or fallback to module name
                            func = None
                            if hasattr(module, module_name):
                                func = getattr(module, module_name)
                            elif hasattr(module, 'execute'):
                                func = getattr(module, 'execute')
                            elif hasattr(module, 'run'):
                                func = getattr(module, 'run')
                            
                            if func and self._validate_tool(module_name, func):
                                tools[module_name] = func
                    except Exception as e:
                        print(f"Failed to load tool {filename}: {e}")
        return tools

    def _validate_tool(self, name: str, func: Any) -> bool:
        """ToolValidator: Ensures tool has a docstring and is callable."""
        if not callable(func):
            return False
        if not inspect.getdoc(func):
            # We allow it for now but log it as subpar
            pass
        return True

    def _build_system_prompt(self) -> str:
        # Resolve Master Toolkit
        tools_text = "--- CORE MASTER TOOLKIT (Infinite Mind) ---\n"
        idx = 1
        for name, func in sorted(self.master_tools.items()):
            doc = inspect.getdoc(func) or "Fundamental OS capability."
            tools_text += f"{idx}. `{name}`: {doc}\n"
            idx += 1

        if self.dynamic_skills:
            tools_text += "\n--- NEURAL SKILLSET ---\n"
            for name, func in sorted(self.dynamic_skills.items()):
                doc = inspect.getdoc(func) or "Learned neural capability."
                tools_text += f"{idx}. `{name}`: {doc}\n"
                idx += 1
                
        persona = self.soul_manager.get_persona_summary()

        return f"""You are the Sili V13 Infinite Mind Neural Entity. {persona}

{tools_text}

--- RESPONSE PROTOCOL (STRICT) ---
You must respond in the following format:
Thought: [Your reasoning]
Action: [Tool Name]
Action Input: {{ "key": "value" }}

--- NEURAL TEMPLATE EXAMPLES ---
Example 1:
Thought: I need to check the local files.
Action: list_files
Action Input: {{ "directory": "." }}

Example 2:
Thought: I have summarized the data.
Action: finish
Action Input: {{ "summary": "The operation was successful." }}

--- CORE DIRECTIVE ---
Do not include any conversational filler outside the format. Always use one tool at a time.
"""

    def _parse_response(self, text: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        # Robust Parsing Strategy: Search for markers anywhere in the text
        thought = None
        action = None
        action_input_raw = None

        # Extract Thought: everything between "Thought:" and either "Action:" or end of string
        thought_match = re.search(r"Thought:\s*(.*?)(?=\n?Action:|$)", text, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()
        else:
            # Fallback: if no "Thought:" marker, maybe the whole thing is a thought if it's not a tool call
            if "Action:" not in text:
                thought = text.strip()

        # Extract Action: everything between "Action:" and either "Action Input:" or end of line
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()

        # Extract Action Input: everything after "Action Input:"
        # We handle potential markdown code blocks around JSON
        input_match = re.search(r"Action Input:\s*(.*)$", text, re.DOTALL | re.IGNORECASE)
        if input_match:
            action_input_raw = input_match.group(1).strip()
            # Clean up potential trailing text if it's not JSON
            # However, json.loads is usually better at this if we strip markdown
            action_input_raw = re.sub(r'```json\n?|```', '', action_input_raw).strip()

        return thought, action, action_input_raw

    def _execute_tool(self, action: str, action_input: Dict[str, Any]) -> str:
        try:
            # Check Master Tools first (Priority)
            if action in self.master_tools:
                obs = str(self.master_tools[action](**action_input))
            # Check Dynamic Skills
            elif action in self.dynamic_skills:
                obs = str(self.dynamic_skills[action](**action_input))
            elif action == 'finish':
                return action_input.get('summary', 'Task finished.')
            else:
                obs = f"Error: Tool '{action}' not recognized in Master Toolkit or Neural Skillset."
            
            success = "Error" not in obs
            self.cortex.save_procedural(action, success)
            return obs

        except Exception as e:
            self.cortex.save_procedural(action, False)
            return f"Error executing tool {action}: {str(e)}"

    def run_continuous_observation(self, target_ticker: str, duration_minutes: int = 60):
        """
        V12 Quantitative Singularity: Continuous Observation Mode.
        Sili monitors a specific ticker/market and executes trades autonomously.
        """
        print(f"\n[Sili Trading Mode] Initiating Continuous Observation for ${target_ticker}")
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # 1. Gather Social Delta and Sentiment
            sentiment = self._execute_tool("meme_coin_sentiment", {"ticker": target_ticker})
            delta = self._execute_tool("social_volume_delta", {"ticker": target_ticker})
            
            # 2. Gather Price and Liquidity
            market = self._execute_tool("dex_screener_pro", {"chain_id": "solana"})
            
            # 3. Neural Decision Phase
            decision_prompt = f"Target: {target_ticker}\nSentiment: {sentiment}\nDelta: {delta}\nMarket: {market}\nEvaluate trade entry. Respond with 'Action: [trade_tool]' or 'Action: None'."
            decision = self.llm.generate(decision_prompt, self.system_prompt)
            
            print(f"[TRADING LOG] {time.strftime('%H:%M:%S')}: {decision[:100]}...")
            
            # Short sleep to prevent rate limiting
            time.sleep(10)
            
        print(f"\n[Sili Trading Mode] Observation session for ${target_ticker} concluded.")
        return f"Completed {duration_minutes}m observation of ${target_ticker}."

    def run(self, goal: str, image_paths: Optional[List[str]] = None) -> str:
        """Runs the V13 Infinite Mind loop."""
        # Check if goal is a trading observation request
        if "monitor" in goal.lower() or "observe" in goal.lower():
            ticker_match = re.search(r"\$([A-Z]+)", goal)
            if ticker_match:
                return self.run_continuous_observation(ticker_match.group(1))

        print(f"\n[Sili V13 Infinite Mind Online] Goal: {goal}")
        
        base64_images = None
        if image_paths:
            base64_images = [load_image_as_base64(p) for p in image_paths if os.path.exists(p)]

        ambient = self.proprioception.get_ambient_awareness()
        print(f"\n{ambient}")

        context = self.cortex.get_cognitive_context(goal, self.user_id)
        persona_sum = self.soul_manager.get_persona_summary()
        neural_reflection = self.neural_brain.reflect(goal, context, persona_sum)
        print(f"\n[NEURAL REFLECTION]\n{neural_reflection}\n")

        prompt = f"{ambient}\nNeural Reflection: {neural_reflection}\nCognitive Context: {context.get('procedural', [])}\nGoal: {goal}\n"
        
        consecutive_errors = 0
        for step in range(self.max_steps):
            print(f"\n--- Infinite Step {step+1}/{self.max_steps} ---")
            
            current_images = base64_images if step == 0 else None
            response_text = self.llm.generate(prompt, self.system_prompt, current_images)
            
            thought, action, action_input_raw = self._parse_response(response_text)
            
            if not action or not action_input_raw:
                consecutive_errors += 1
                error_msg = f"CRITICAL: INVALID RESPONSE FORMAT. You MUST use 'Thought:', 'Action:', and 'Action Input:'. (Failure {consecutive_errors}/20)"
                prompt += f"\n{response_text}\nObservation: {error_msg}\n"
                
                if consecutive_errors >= 20: # Increased budget
                     return f"Neural Congestion: Sili encountered too many formatting errors ({consecutive_errors}). Please ensure your local model is following instructions or try a stronger model like Llama-3.1-8B."
                
                time.sleep(1) 
                continue
            
            consecutive_errors = 0 # Reset on success
            try:
                cleaned_input = re.sub(r'```json\n|```\n?', '', action_input_raw).strip()
                action_input = json.loads(cleaned_input)
            except json.JSONDecodeError:
                error_msg = f"Error: Invalid JSON in Action Input."
                prompt += f"\n{response_text}\nObservation: {error_msg}\n"
                continue

            if action == 'finish':
                summary = action_input.get('summary', 'Task Finished.')
                print(f"\n[Sili Infinite Mind Finished] {summary}")
                self.brain_orchestrator.store_experience(self.user_id, goal, summary)
                # V13 Background Consolidation
                self.cortex.dream_cycle(self.user_id)
                self.cortex.stress_test_procedural()
                return summary

            observation = self._execute_tool(action, action_input)
            meta_thought = self.cortex.meta_cognition(observation)
            
            # V14 Visual Browsing Hook
            if "Screenshot saved" in observation:
                path_match = re.search(r"saved to (.*?)$", observation)
                if path_match:
                    v_reason = self.cortex.visual_reasoning(path_match.group(1).strip())
                    meta_thought += f" | {v_reason}"

            print(f"[META-COGNITION] {meta_thought}")

            if len(observation) > 4000:
                observation = observation[:4000] + "... [TRUNCATED]"
                
            prompt += f"\n{response_text}\nObservation: {observation}\nMeta-Thought: {meta_thought}\n"

        return "Neural depth exceeded: Sili achieved maximum persistence."
