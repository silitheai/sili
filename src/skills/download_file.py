import requests
import os

def download_file(url: str, save_path: str = None) -> str:
    """Directly downloads a file from the internet to your local disk."""
    try:
        if not save_path:
             filename = url.split('/')[-1]
             if not filename or "?" in filename:
                  filename = "downloaded_file.tmp"
             save_path = os.path.join(os.getcwd(), filename)
             
        # Stream download to avoid massive RAM blobs on big files
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        return f"Download complete! File saved successfully to:\n{os.path.abspath(save_path)}"
        
    except requests.exceptions.Timeout:
         return f"Error: The download connection timed out."
    except Exception as e:
         return f"Failed to download file: {str(e)}"
