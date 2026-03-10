import psutil

def system_stats() -> str:
    """Returns the current CPU, Memory, and Disk usage of the host server."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = (
            f"--- Host System Status ---\n"
            f"CPU Usage: {cpu}%\n"
            f"RAM Usage: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)\n"
            f"Disk Usage: {disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)"
        )
        return stats
    except Exception as e:
        return f"Error fetching system stats: {str(e)}"
