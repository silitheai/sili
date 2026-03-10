import os

def image_metadata_extractor(image_path: str) -> str:
    """Extracts raw string EXIF/metadata headers from a local image file using binary parsing."""
    if not os.path.exists(image_path):
        return f"Error: Image '{image_path}' not found."
        
    try:
        # Instead of pulling in PIL or ExifRead just for this core task, we can do a raw byte search for printable metadata blocks
        # This is often enough to find copyright, camera models, and software tags
        with open(image_path, 'rb') as f:
            data = f.read(4000) # Read the first 4KB (Usually contains headers EXIF/JFIF/PNG chunks)
            
        printable_chars = set(bytes('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_., !?()/:', 'ascii'))
        
        strings = []
        current_string = []
        
        for byte in data:
            if byte in printable_chars:
                current_string.append(chr(byte))
            else:
                if len(current_string) >= 5: # Only keep strings longer than 4 chars
                    strings.append("".join(current_string))
                current_string = []
                
        if len(current_string) >= 5:
            strings.append("".join(current_string))
            
        # Filter noise
        clean_strings = [s for s in strings if not all(c == ' ' for c in s) and "IDAT" not in s]
        
        if not clean_strings:
             return f"No readable metadata strings found in the header of '{image_path}'."
             
        output = f"--- RAW METADATA BLOCKS FOR '{os.path.basename(image_path)}' ---\n"
        for i, val in enumerate(clean_strings, 1):
            output += f"Block {i}: {val.strip()}\n"
            
        return output
        
    except Exception as e:
        return f"Error extracting metadata: {e}"
