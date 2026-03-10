import subprocess
import os

def execute_bash(command: str) -> str:
    """Executes a bash command on the Ubuntu server and returns the output.
    Use this to run terminal tools, check system state, install dependencies, or interact with APIs.
    
    Args:
        command: The bash command to execute (e.g. 'ls -la', 'uname -a', 'python script.py').
    """
    try:
        # Run command securely but with environment access
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
            
        return output.strip() if output else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"
