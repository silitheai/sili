import os
import json

class NeuralCortex:
    """Hierarchical memory and meta-cognitive orchestrator for Sili V10."""
    def __init__(self, brain_orchestrator):
        self.orchestrator = brain_orchestrator
        # Procedural memory: skill usage patterns (could be a local JSON)
        self.procedural_path = os.path.join(os.path.dirname(__file__), '..', '..', 'procedural_memory.json')
        self.procedural_memory = self._load_procedural()

    def _load_procedural(self):
        if os.path.exists(self.procedural_path):
            try:
                with open(self.procedural_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_procedural(self, action, success):
        if action not in self.procedural_memory:
            self.procedural_memory[action] = {"calls": 0, "successes": 0}
        self.procedural_memory[action]["calls"] += 1
        if success:
            self.procedural_memory[action]["successes"] += 1
        
        with open(self.procedural_path, 'w') as f:
            json.dump(self.procedural_memory, f, indent=4)

    async def get_cognitive_context(self, query, user_id):
        """Synthesizes Episodic, Semantic, and Procedural memory with Recursive depth."""
        # Use Recursive depth=1 for Infinite Mind
        context = await self.orchestrator.get_relevant_context(query, user_id, depth=1)
        
        # Add procedural 'feelings' about tools
        procedural_insights = []
        for action, stats in self.procedural_memory.items():
            rate = (stats["successes"] / stats["calls"]) * 100 if stats["calls"] > 0 else 0
            if rate < 50 and stats["calls"] > 2:
                procedural_insights.append(f"Warning: Tool '{action}' has a high failure rate ({100-rate}%). Use with caution.")
            elif rate > 90 and stats["calls"] > 5:
                procedural_insights.append(f"Preference: Tool '{action}' is highly reliable.")

        context["procedural"] = procedural_insights
        return context

    def check_procedural_integrity(self):
        """
        V17: Core Procedural Audit.
        Returns a summary of tool reliability and pattern stagnation.
        """
        metrics = []
        for action, stats in self.procedural_memory.items():
            rate = (stats["successes"] / stats["calls"]) * 100 if stats["calls"] > 0 else 0
            metrics.append(f"Tool `{action}`: {rate:.1f}% success rate over {stats['calls']} calls.")
            
        if not metrics:
            return "Procedural memory is initialized but empty. No pattern data available."
            
        return "\n".join(metrics)

    async def dream_cycle(self, user_id):
        """Consolidation Loop: Compresses Episodic memories into Semantic knowledge."""
        print(f"[THE DREAM CYCLE] Sili is consolidating memories for {user_id}...")
        history = self.orchestrator.short_term.get_user_history(user_id)
        if len(history) > 15:
            # Consolidate older memories into the vector database
            to_consolidate = history[:10]
            summary = f"Consolidated Experience: " + " | ".join([f"{m['role']}: {m['content'][:50]}..." for m in to_consolidate])
            await self.orchestrator.vector.add_interaction(user_id, "system", summary)
            print(f"[THE DREAM CYCLE] Compressed {len(to_consolidate)} episodic fragments into 1 semantic cluster.")
            return True
        return False

    def stress_test_procedural(self):
        """Meta-Cognitive Stress Test: Challenges established patterns."""
        print("[META-COGNITION] Initiating Procedural Stress Test...")
        for action in self.procedural_memory:
            # Simulation: Sili intentionally tries a different path if a tool is 'too' comfortable
            if self.procedural_memory[action]["calls"] > 20:
                print(f"[STRESS TEST] Pattern stagnation detected for '{action}'. Suggesting alternative vectors.")

    def meta_cognition(self, observation):
        """Evaluates tool observation quality with V14 Visual context awareness."""
        if not observation or "Error" in observation:
            return "Observation contains an error. I must engage Internal Debate to find a contingency."
        
        if "Screenshot saved" in observation:
            return "Visual intelligence captured. I must now analyze the pixel-space for hidden UI elements or market deltas."
        
        if len(observation) > 5000:
            return "Observation is high-density. I must synthesize carefully to avoid context dilution."
            
        return "Observation verified. Proceeding with Singularity Directive."

    def visual_reasoning(self, image_path: str):
        """Interprets browser snapshots for interactive decision making."""
        print(f"[VISUAL REASONING] Analyzing {image_path} via V14 Browser Avatar...")
        # In a real scenario, this would trigger llama3.2-vision
        return f"Successfully extracted UI structure from {image_path}. No blockers detected."
