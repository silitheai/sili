import requests

def expand_short_url(short_url: str) -> str:
    """Expands a shortened URL (like bit.ly or tinyurl) to reveal its final hidden destination."""
    try:
        # We make a HEAD request and don't allow redirects, reading the Location header implicitly via history
        res = requests.head(short_url, allow_redirects=True, timeout=10)
        final_url = res.url
        
        if final_url == short_url:
             return f"The URL '{short_url}' is not a redirect, or the destination could not be resolved further."
             
        # Check if there were multiple hops
        hops = [r.url for r in res.history]
        hop_string = " -> ".join(hops) if hops else "Direct"
        
        output = f"--- URL EXPANSION FOR '{short_url}' ---\n"
        output += f"Final Destination: {final_url}\n"
        output += f"Redirect Path: {hop_string}"
        
        return output
        
    except requests.exceptions.Timeout:
         return "Connection timed out trying to resolve redirect."
    except Exception as e:
        return f"Failed to expand URL: {e}"
