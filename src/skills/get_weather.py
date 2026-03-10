import requests

def get_weather(location: str) -> str:
    """Fetches the current weather for a specified location using wttr.in."""
    try:
        # Use format 3 for concise plain text, format 4 for one-line + wind
        url = f"https://wttr.in/{location}?format=3"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
