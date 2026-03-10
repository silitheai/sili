import PyPDF2
import os

def read_pdf(file_path: str, max_pages_to_read: int = 15) -> str:
    """Reads raw text from a local PDF file."""
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' does not exist on disk."
        
    try:
        text = f"--- Content of {os.path.basename(file_path)} ---\n"
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Prevent infinite processing
            pages_to_process = min(total_pages, max_pages_to_read)
            
            for i in range(pages_to_process):
                page = reader.pages[i]
                text += f"\n[Page {i+1}]\n"
                text += page.extract_text()
                
            if total_pages > max_pages_to_read:
                text += f"\n... [Truncated! Stopped at page {max_pages_to_read} out of {total_pages}]"
                
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"
