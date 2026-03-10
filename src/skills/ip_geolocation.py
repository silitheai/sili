import requests

def ip_geolocation(ip_address: str) -> str:
    """Looks up the physical geolocation and ISP data of an IP address."""
    try:
        # Using ip-api.com free tier (no api key required)
        url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'fail':
            return f"Lookup Failed: {data.get('message', 'Unknown error')}"
            
        report = (
            f"Geolocation Info for {ip_address}:\n"
            f"Country: {data.get('country')}\n"
            f"Region/City: {data.get('regionName')}, {data.get('city')} {data.get('zip')}\n"
            f"Coordinates: {data.get('lat')}, {data.get('lon')}\n"
            f"Timezone: {data.get('timezone')}\n"
            f"ISP/Org: {data.get('isp')} / {data.get('org')}\n"
            f"ASN: {data.get('as')}"
        )
        return report
        
    except Exception as e:
        return f"Error conducting geolocation on {ip_address}: {e}"
