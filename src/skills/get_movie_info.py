import requests
import urllib.parse

def get_movie_info(movie_title: str) -> str:
    """Searches for detailed metadata (cast, genre, imdb rating, plot) about a movie using the public OMDB API."""
    try:
        # A public unofficial OMDB key that works for small testing loads.
        # Alternatively we could scrape Wikipedia, but an API is much cleaner for film logic
        api_key = "fe309ba8" 
        
        safe_title = urllib.parse.quote(movie_title)
        url = f"http://www.omdbapi.com/?t={safe_title}&apikey={api_key}"
        
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        if data.get('Response') == 'False':
             return f"Movie search failed: {data.get('Error', 'Movie not found.')}"
             
        output = f"🎬 --- METADATA FOR '{data.get('Title').upper()}' ({data.get('Year')}) ---\n"
        output += f"Rated: {data.get('Rated')} | Runtime: {data.get('Runtime')} | Genre: {data.get('Genre')}\n"
        output += f"Director: {data.get('Director')}\n"
        output += f"Writer: {data.get('Writer')}\n"
        output += f"Actors: {data.get('Actors')}\n"
        output += "-" * 50 + "\n"
        output += f"Plot Summary: {data.get('Plot')}\n"
        output += "-" * 50 + "\n"
        output += f"Box Office: {data.get('BoxOffice', 'N/A')}\n"
        
        # Get ratings
        for r in data.get('Ratings', []):
            output += f"- {r['Source']}: {r['Value']}\n"
            
        if 'imdbRating' in data and data['imdbRating'] != 'N/A':
             output += f"IMDB Rating Total: {data['imdbRating']}/10 (from {data.get('imdbVotes', 0)} votes)\n"
             
        return output
    except Exception as e:
        return f"Error trying to fetch movie metadata: {e}"
