import tempfile
import subprocess
import os

def execute_python_code(code: str) -> str:
    """Writes dynamic python code to a temporary file and executes it.
    This gives the agent the ability to do "anything", including data analysis, 
    making complex API calls (like trading), or advanced web scraping.
    
    Args:
        code: Complete Python script to execute.
    """
    try:
        # Create a temporary file to hold the script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        # Execute the python script securely but with full environment access
        result = subprocess.run(
            [sys.executable or 'python3', temp_path],
            capture_output=True,
            text=True,
            timeout=30 # Prevents infinite loops
        )
        
        # Clean up the script
        os.unlink(temp_path)
        
        output = result.stdout
        if result.stderr:
            output += f"\n[Errors/Warnings]:\n{result.stderr}"
            
        return output.strip() if output else "Script executed successfully with no output."
        
    except subprocess.TimeoutExpired:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return "Error: Script execution timed out after 30 seconds."
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return f"Error executing python code: {str(e)}"
