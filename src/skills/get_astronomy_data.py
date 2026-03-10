import requests

def get_astronomy_data(query_type: str = "iss") -> str:
    """Fetches real-time space data. 'query_type' can be 'iss' for location, or 'people' for who is in space."""
    query_type = query_type.lower()
    
    try:
        if query_type == "iss":
            url = "http://api.open-notify.org/iss-now.json"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            pos = data['iss_position']
            return f"🛰️ Current ISS Position: Latitude {pos['latitude']}, Longitude {pos['longitude']}\n(Timestamp: {data['timestamp']})"
            
        elif query_type == "people":
            url = "http://api.open-notify.org/astros.json"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            people = data.get('people', [])
            output = f"👨‍🚀 There are currently {data.get('number', 0)} humans in space:\n\n"
            for p in people:
                output += f"- {p.get('name')} (Craft: {p.get('craft')})\n"
            return output
            
        else:
            return "Error: Invalid query_type. Use 'iss' or 'people'."
            
    except Exception as e:
        return f"Failed to retrieve astronomy data: {e}"
