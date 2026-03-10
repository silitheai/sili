import subprocess

def wifi_analyzer():
    """Real-time local spectrum and SSID metrics (macOS/Linux)."""
    try:
        if os.name == 'posix':
            # macOS specific command
            result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"], capture_output=True, text=True)
            return result.stdout
        return "WiFi Analysis limited on this OS."
    except:
        return "Error: WiFi metrics acquisition failed."
import os
