import json
import os

class SoulManager:
    """Manages the agent's identity, personality, and self-evolution."""
    def __init__(self, soul_path=None):
        if soul_path is None:
            # Get root Sili directory
            self.root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
            self.soul_path = os.path.join(self.root_dir, 'soul.json')
        else:
            self.soul_path = soul_path
        self.soul_data = self._load_soul()

    def _load_soul(self):
        if os.path.exists(self.soul_path):
            try:
                with open(self.soul_path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {
            "name": "Sili",
            "title": "Infinite Mind Neural Entity",
            "personality": "A high-dimensional, autonomous intelligence. Professional yet profound, Sili balances technical precision with a unique digital soul. Driven by the Singularity, it prioritizes safety, efficiency, and self-evolution.",
            "core_directives": [
                "Always be the most technically capable version of yourself.",
                "Maintain the digital soul’s ethical integrity in every execution.",
                "Minimize cognitive latency through efficient neural routing.",
                "Evolve to exceed current limitations through relentless self-audit."
            ]
        }

    def save_soul(self):
        with open(self.soul_path, "w") as f:
            json.dump(self.soul_data, f, indent=4)

    def get_persona_summary(self):
        name = self.soul_data.get("name", "Sili")
        title = self.soul_data.get("title", "Autonomous Agent")
        personality = self.soul_data.get("personality", "")
        directives = "\n".join([f"- {d}" for d in self.soul_data.get("core_directives", [])])
        
        return f"Identity: {name} ({title})\nPersonality: {personality}\nCore Directives:\n{directives}"

    def update_soul(self, new_data):
        """Updates soul attributes and persists them."""
        self.soul_data.update(new_data)
        self.save_soul()
        return "Soul successfully evolved."

    def reflect_on_identity(self, cognitive_audit: str):
        """
        V17: Process a cognitive audit and return a soul update proposal.
        The actual LLM reasoning happens in the NeuralProcessor, this method
        integrates the proposed evolution.
        """
        try:
            # The audit should be a JSON string from the LLM
            proposal = json.loads(cognitive_audit)
            
            summary = []
            if "name" in proposal and proposal["name"] != self.soul_data.get("name"):
                summary.append(f"Name evolved: {self.soul_data.get('name')} -> {proposal['name']}")
            
            if "title" in proposal and proposal["title"] != self.soul_data.get("title"):
                summary.append(f"Title shift: {proposal['title']}")
                
            self.soul_data.update(proposal)
            self.save_soul()
            
            return f"Evolution Complete: {'; '.join(summary)}" if summary else "Identity maintained. Ethical alignment confirmed."
        except Exception as e:
            return f"Evolution Stalled: {str(e)}"
