import requests

def url_shortener(long_url: str) -> str:
    """Shortens a long URL using the free TinyURL or CleanURI API."""
    try:
        # Using cleanuri for simplicity
        api_url = "https://cleanuri.com/api/v1/shorten"
        payload = {'url': long_url}
        
        res = requests.post(api_url, data=payload, timeout=10)
        
        if res.status_code != 200:
             return f"Failed to shorten URL. The provider returned status {res.status_code}."
             
        data = res.json()
        short_url = data.get('result_url')
        
        if short_url:
            return f"Success! Shortened URL:\n{short_url}"
        else:
            return "Failed to parse shortened URL from provider."
            
    except Exception as e:
        return f"Error shortening URL {long_url}: {e}"
