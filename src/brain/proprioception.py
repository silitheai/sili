import psutil
import socket
import os
import datetime
import time

class Proprioception:
    """Manages the agent's OS awareness and V13 Cognitive Meta-Metrics."""
    def __init__(self):
        self._cache = None
        self._last_check = 0
        self._cache_duration = 60 # Seconds

    def get_ambient_awareness(self):
        """Returns a cached snapshot of the 'physical' and 'neural' state."""
        current_time = time.time()
        if self._cache and (current_time - self._last_check < self._cache_duration):
            return self._cache

        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        uptime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        hostname = socket.gethostname()
        processes = len(psutil.pids())
        
        # Neural Meta-Metrics
        neural_load = self.get_cognitive_load()

        awareness = f"""[AMBIENT AWARENESS]
Host: {hostname} (Uptime: {uptime})
Neural Load: {neural_load['status']} ({neural_load['context_usage']} context)
System State: {cpu_usage}% CPU, {memory.percent}% RAM, {disk.percent}% Disk used.
Active Neural Processes: {processes}
Time: {datetime.datetime.now().strftime("%H:%M:%S")}
"""
        self._cache = awareness
        self._last_check = current_time
        return awareness

    def get_cognitive_load(self):
        """Measures cognitive proprioception: internal neural state."""
        import random
        # Simulation of neural pressure metrics for V13
        latency = random.uniform(0.5, 1.8)
        context_usage = random.randint(2000, 12000)
        
        status = "OPTIMAL"
        if context_usage > 10000:
            status = "CRITICAL (Context Pressure)"
        elif latency > 1.5:
            status = "CONGESTED (Neural Latency)"
            
        return {
            "status": status,
            "latency": f"{latency:.2f}s",
            "context_usage": f"{context_usage} tokens"
        }

    def check_anomalies(self):
        """Passive check for system stress."""
        awareness = self.get_ambient_awareness()
        return awareness
