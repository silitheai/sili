import sys
import os

# Ensure src is in path so we can import Agent
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def spawn_sub_agent(sub_task_goal: str) -> str:
    """Spawns a temporary, independent sub-agent to accomplish a complex sub-task. The sub-agent runs autonomously and returns its final report."""
    try:
        from src.agent import Agent
        
        # Instantiate a fresh agent for this specific sub-task
        # We use a specific sub-agent ID so its short-term memory doesn't collide with the main agent
        sub_agent = Agent(user_id="sub_agent_worker")
        
        # Run the sub-agent synchronously
        # Prepend a strict directive to make it focus on returning data
        directive = f"[SUB-AGENT DIRECTIVE] You are a specialized worker spawned to complete the following task. Do your job flawlessly and return the exact requested data in your final 'finish' summary:\n\nTASK: {sub_task_goal}"
        
        result_summary = sub_agent.run(directive)
        
        return f"--- SUB-AGENT EXECUTION COMPLETE ---\nResult:\n{result_summary}"
        
    except ImportError:
        return "Core error: Failed to import the Agent module for cloning."
    except Exception as e:
        return f"Sub-agent encountered a catastrophic failure: {str(e)}"
