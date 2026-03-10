import psutil
import shutil
import time

def system_health_check() -> str:
    """Performs a comprehensive check of the host machine's vital statistics: Disk, Network IO, Memory, and Boot Time."""
    try:
        output = "--- RAPID HOST HEALTH DIAGNOSTICS ---\n\n"
        
        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        output += f"[CPU]\n- Cores: {psutil.cpu_count(logical=True)} logical\n- Current Load: {cpu_usage}%\n\n"
        
        # RAM
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        avail_gb = mem.available / (1024 ** 3)
        output += f"[MEMORY]\n- Total RAM: {total_gb:.2f} GB\n- Available: {avail_gb:.2f} GB\n- Used: {mem.percent}%\n\n"
        
        # DISK
        total, used, free = shutil.disk_usage("/")
        output += f"[DISK (root /)]\n- Total Space: {(total / (1024**3)):.2f} GB\n- Free Space: {(free / (1024**3)):.2f} GB\n\n"
        
        # NETWORK SPEED (Basic IO over 1 sec)
        net1 = psutil.net_io_counters()
        time.sleep(1)
        net2 = psutil.net_io_counters()
        
        dl_speed = (net2.bytes_recv - net1.bytes_recv) / 1024 # KB/s
        up_speed = (net2.bytes_sent - net1.bytes_sent) / 1024 # KB/s
        
        output += f"[NETWORK I/O (Current Traffic)]\n- Download: {dl_speed:.2f} KB/s\n- Upload: {up_speed:.2f} KB/s\n\n"
        
        # UPTIME
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        output += f"[SYSTEM UPTIME]\n- Machine Booted At: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return output
        
    except Exception as e:
        return f"Diagnostics encountered a severe failure: {e}"
        
from datetime import datetime
