import re
from bs4 import BeautifulSoup

def html_to_markdown(html_text: str) -> str:
    """Converts raw or messy HTML code back into clean, readable Markdown."""
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Very rudimentary html-to-md converter for basic reading
        # Remove scripts/styles
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.extract()
            
        # Convert Headings
        for i in range(1, 7):
            for h in soup.find_all(f'h{i}'):
                 h.replace_with(f"\n{'#' * i} {h.get_text().strip()}\n")
                 
        # Convert links
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text().strip()
            a.replace_with(f"[{text}]({href})")
            
        # Convert lists
        for ul in soup.find_all('ul'):
             for li in ul.find_all('li'):
                  li.replace_with(f"- {li.get_text().strip()}\n")
             ul.unwrap()
             
        for ol in soup.find_all('ol'):
             for i, li in enumerate(ol.find_all('li'), 1):
                  li.replace_with(f"{i}. {li.get_text().strip()}\n")
             ol.unwrap()
             
        # Extract text
        md_text = soup.get_text(separator=' ')
        
        # Cleanup excess whitespace
        md_text = re.sub(r'\n\s*\n', '\n\n', md_text).strip()
        
        if len(md_text) > 20000:
            md_text = md_text[:20000] + "\n... [TRUNCATED]"
            
        return f"--- EXTRACTED MARKDOWN ---\n{md_text}"
        
    except Exception as e:
        return f"Failed to parse HTML to Markdown: {e}"
