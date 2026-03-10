import hashlib
import os

def generate_file_hash(file_path: str, hash_type: str = 'sha256') -> str:
    """Calculates the cryptographic hash (sha256/md5) of a local file."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
        
    try:
        if hash_type.lower() == 'md5':
            hash_func = hashlib.md5()
        else:
            hash_func = hashlib.sha256()
            
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
                
        return f"FILE HASH ({hash_type.upper()}) for '{file_path}':\n{hash_func.hexdigest()}"
        
    except Exception as e:
        return f"Error computing file hash: {str(e)}"
