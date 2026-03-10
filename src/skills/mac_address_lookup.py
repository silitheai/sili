import requests

def mac_address_lookup(mac_address: str) -> str:
    """Looks up the device manufacturer (Vendor) for a given MAC hardware address."""
    # Free OUI MAC API
    url = f"https://api.macvendors.com/{mac_address}"
    
    try:
        # MAC Vendors limits requests heavily, so 5s timeout
        response = requests.get(url, timeout=5)
        
        if response.status_code == 404:
            return f"MAC Address Prefix ({mac_address}) not recognized or vendor is unassigned."
        elif response.status_code == 429:
            return "Error: Reached MAC OUI lookup API rate limit. Please wait."
            
        response.raise_for_status()
        vendor = response.text
        return f"The vendor for MAC address {mac_address} is: {vendor}"
        
    except Exception as e:
        return f"Failed to lookup MAC OUI vendor: {str(e)}"
