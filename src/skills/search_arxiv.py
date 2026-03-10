import urllib.request
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 3) -> str:
    """Searches the ArXiv academic database for scientific papers and returns their titles, authors, and abstract summaries."""
    try:
        # ArXiv API uses a specific query format
        query = query.replace(' ', '+')
        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            
        # Parse XML
        root = ET.fromstring(xml_data)
        
        # XML Namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            return f"No academic papers found on ArXiv for query: '{query}'"
            
        output = f"--- ArXiv ACADEMIC SEARCH RESULTS FOR '{query}' ---\n\n"
        
        for i, entry in enumerate(entries, 1):
             title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
             summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
             link = entry.find('atom:id', ns).text
             
             authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
             author_str = ", ".join(authors)
             
             output += f"{i}. {title}\n"
             output += f"Authors: {author_str}\n"
             output += f"Link: {link}\n"
             output += f"Abstract: {summary[:400]}...\n\n"
             
        return output
        
    except Exception as e:
        return f"Error fetching data from ArXiv: {e}"
