import os
import glob

def read_file(path: str) -> str:
    """Reads the contents of a file.
    
    Args:
        path: The absolute or relative path to the file.
    """
    try:
        # V16.15: Added safety limit (Limit to 1MB)
        file_size = os.path.getsize(path)
        if file_size > 1024 * 1024:
             return f"Error: File is too large ({file_size} bytes). Sili restricts reading to 1MB to prevent neural congestion."
             
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file, overwriting it if it exists.
    
    Args:
        path: The path to the file.
        content: The content to write.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_files(path: str) -> str:
    """Lists files and directories in a given path.
    
    Args:
        path: The directory path to list.
    """
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"
