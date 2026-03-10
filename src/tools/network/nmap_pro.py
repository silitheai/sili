import subprocess

def nmap_pro(target: str, scan_type: str = "-sV"):
    """Advanced network service & vulnerability scanning using nmap."""
    try:
        result = subprocess.run(["nmap", scan_type, target], capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error: nmap failed. {result.stderr}"
        return result.stdout
    except FileNotFoundError:
        return "Error: nmap not installed on host."
