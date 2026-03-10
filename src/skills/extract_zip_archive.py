import shutil
import os

def extract_zip_archive(zip_file_path: str, extract_to_dir: str = None) -> str:
    """Extracts a ZIP archive file into a target directory."""
    if not os.path.exists(zip_file_path):
        return f"Error: ZIP file '{zip_file_path}' does not exist."
        
    if not zip_file_path.endswith('.zip'):
         return f"Warning: '{zip_file_path}' does not have a .zip extension, extraction might fail."
         
    try:
        if not extract_to_dir:
             # Default to extracting to a folder with the same name as the zip
             extract_to_dir = zip_file_path[:-4] if zip_file_path.endswith('.zip') else zip_file_path + "_extracted"
             
        os.makedirs(extract_to_dir, exist_ok=True)
        shutil.unpack_archive(zip_file_path, extract_to_dir, 'zip')
        
        return f"Success! ZIP archive '{zip_file_path}' has been fully uncompressed.\nContents extracted to: {extract_to_dir}"
        
    except Exception as e:
         return f"Failed to extract ZIP archive: {e}"
