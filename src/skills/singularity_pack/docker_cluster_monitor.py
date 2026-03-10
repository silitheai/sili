import subprocess

def docker_cluster_monitor():
    """Manages and monitors local Docker container orchestration."""
    try:
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"], capture_output=True, text=True)
        if result.returncode != 0:
            return "Error: Docker daemon not reachable or permissions denied."
        return f"Sili Neural Container Monitor:\n{result.stdout}"
    except:
        return "Error: Docker is not installed on the host system."
