import subprocess
import platform

def ping_host(host: str, count: int = 4) -> str:
    """Sends ICMP Echo Requests (Pings) to a specified IP address or Domain Name to determine network reachability."""
    try:
        # Determine current OS platform to select the correct ping argument
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        # Build command dynamically based on OS
        command = ['ping', param, str(count), host]
        
        # Execute securely via subprocess list
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        
        if result.returncode == 0:
            return f"Ping Result for {host}:\n{result.stdout}"
        else:
            return f"Host {host} is unreachable or timed out.\nError:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
         return f"Ping to {host} automatically timed out after 10 seconds. Host may be offline or blocking ICMP packets."
    except Exception as e:
         return f"Failed to execute ping logic: {str(e)}"
