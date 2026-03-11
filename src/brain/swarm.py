import asyncio
from typing import List, Dict, Any, Optional
from src.agent import Agent

class SwarmOrchestrator:
    """
    V18: Advanced Multi-Agent Swarm Orchestration.
    Manages specialized sub-agents to achieve parallel complex goals.
    """
    def __init__(self, master_agent: Agent):
        self.master = master_agent
        self.active_swarm: Dict[str, Agent] = {}
        
    async def summon_specialist(self, specialist_name: str, role_description: str, goal: str) -> str:
        """Spawns an asynchronous sub-agent with a dedicated role and goal."""
        print(f"[SWARM] Summoning specialist '{specialist_name}' for task: {goal[:50]}...")
        
        # Instantiate a fresh clerk agent
        # We don't inherit the master's soul, we give it a specialist persona
        sub_agent = Agent(user_id=f"swarm_{specialist_name}")
        
        # Override the specialist's persona manually for this task
        sub_agent.soul_manager.update_soul({
            "name": specialist_name,
            "title": f"Specialist Swarm Agent: {specialist_name}",
            "personality": f"Hyper-focused, efficient, and direct. Specialist role: {role_description}",
            "core_directives": ["Complete the assigned sub-goal flawlessly.", "Summarize results with maximum precision."]
        })
        
        self.active_swarm[specialist_name] = sub_agent
        
        # Execute the goal
        result = await sub_agent.run(goal)
        
        # Clean up
        del self.active_swarm[specialist_name]
        return result

    async def execute_parallel_goals(self, goals: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Runs multiple specialists in parallel and returns their aggregated reports.
        Input: [{'name': 'Researcher', 'role': 'Web Search', 'goal': 'Find X'}, ...]
        """
        tasks = []
        for goal_cfg in goals:
            tasks.append(self.summon_specialist(
                goal_cfg['name'], 
                goal_cfg['role'], 
                goal_cfg['goal']
            ))
            
        results = await asyncio.gather(*tasks)
        
        report = {}
        for i, goal_cfg in enumerate(goals):
            report[goal_cfg['name']] = results[i]
            
        return report

    def synthesize_swarm_reports(self, reports: Dict[str, str]) -> str:
        """Synthesizes multiple specialist reports into a single cohesive observation."""
        synthesis = "[SWARM SYNTHESIS REPORT]\n"
        for specialist, report in reports.items():
            synthesis += f"\n--- {specialist} Output ---\n{report}\n"
        return synthesis
