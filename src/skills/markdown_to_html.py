import markdown

def markdown_to_html(markdown_text: str) -> str:
    """Converts raw Markdown text into semantic HTML format."""
    try:
        # Convert with basic extensions for tables and fenced code
        html_output = markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'])
        
        # Don't overload the context
        if len(html_output) > 20000:
             return html_output[:20000] + "\n... [HTML TRUNCATED DUE TO LENGTH]"
             
        return f"--- COMPILED HTML ---\n{html_output}"
        
    except Exception as e:
        return f"Failed to parse markdown: {e}"
