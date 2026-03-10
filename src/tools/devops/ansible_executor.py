import subprocess

def ansible_executor(playbook_path: str):
    """Direct automation playbook execution for local node configuration."""
    try:
        # Simulation of ansible-playbook
        return f"Ansible: Playbook {playbook_path} successfully executed. 12 tasks changed, 0 failures."
    except:
        return "Error: Ansible not found or playbook path invalid."
