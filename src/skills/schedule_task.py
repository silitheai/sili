import json
import os
import uuid
from datetime import datetime

def schedule_task(cron_expression: str, goal: str, user_id: str = "default_user") -> str:
    """Schedules a recurring task for the agent to compute autonomously based on a cron expression (e.g. '0 8 * * *' for every day at 8 AM)."""
    try:
        jobs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jobs.json")
        
        jobs = []
        if os.path.exists(jobs_file):
            try:
                with open(jobs_file, "r") as f:
                    jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
                
        job_id = str(uuid.uuid4())[:8]
        new_job = {
            "id": job_id,
            "cron": cron_expression,
            "goal": goal,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        jobs.append(new_job)
        
        with open(jobs_file, "w") as f:
            json.dump(jobs, f, indent=4)
            
        return f"Job Scheduled Successfully!\nJob ID: {job_id}\nCron: {cron_expression}\nGoal: {goal}\n\nThe background daemon will evaluate this schedule and spontaneously spawn an agent to complete it when triggered."

    except Exception as e:
        return f"Failed to schedule temporal task: {e}"
