import psutil

def thermal_core():
    """Real-time hardware temperature monitors for CPU and GPU."""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return "No temperature sensors found on this host."
        return str(temps)
    except:
        return "Error: Could not retrieve temperature data."
