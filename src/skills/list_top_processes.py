import psutil

def list_top_processes(limit: int = 10, sort_by: str = 'cpu') -> str:
    """Lists the top consuming system processes running on the host OS, sorted by 'cpu' or 'memory'."""
    try:
        attrs = ['pid', 'name', 'cpu_percent', 'memory_info']
        
        # Iterate over all running process
        processes = []
        for p in psutil.process_iter(attrs):
             try:
                 pinfo = p.info
                 
                 # Some processes restrict access
                 if pinfo['memory_info'] is None:
                     continue
                     
                 processes.append({
                     'pid': pinfo['pid'],
                     'name': pinfo['name'],
                     'cpu': pinfo['cpu_percent'] or 0.0,
                     'mem_mb': pinfo['memory_info'].rss / (1024 * 1024)
                 })
             except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                 pass
                 
        # Sort accordingly
        if sort_by.lower() == 'memory':
            processes_sorted = sorted(processes, key=lambda x: x['mem_mb'], reverse=True)
            sort_label = "Memory (MB)"
        else:
            processes_sorted = sorted(processes, key=lambda x: x['cpu'], reverse=True)
            sort_label = "CPU (%)"
            
        # Top N
        top_procs = processes_sorted[:limit]
        
        output = f"--- TOP {len(top_procs)} SYSTEM PROCESSES (Sorted by {sort_label}) ---\n"
        output += f"{'PID':<8} | {'CPU%':<8} | {'RAM (MB)':<10} | {'NAME'}\n"
        output += "-" * 50 + "\n"
        
        for proc in top_procs:
            output += f"{proc['pid']:<8} | {proc['cpu']:<8.1f} | {proc['mem_mb']:<10.1f} | {proc['name']}\n"
            
        return output
    except Exception as e:
        return f"Error retrieving process data: {e}"
