import requests
import urllib.parse

def search_wikipedia(query: str) -> str:
    """Searches Wikipedia and returns the summary of the best matching page."""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=True&explaintext=True&redirects=1&titles={urllib.parse.quote(query)}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        pages = response.json().get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                return f"No Wikipedia page found for '{query}'"
            return page_data.get("extract", "No summary available.")
            
        return "No results."
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"
