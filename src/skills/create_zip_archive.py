import shutil
import os

def create_zip_archive(source_dir: str, output_zip_path: str = None) -> str:
    """Compresses a target directory into a ZIP archive file."""
    if not os.path.exists(source_dir):
        return f"Error: Source directory '{source_dir}' does not exist."
        
    if not os.path.isdir(source_dir):
         return f"Error: '{source_dir}' is a file, not a directory. This skill zips directories."
         
    try:
        if not output_zip_path:
             # Default to compressing it right next to the source
             output_zip_path = source_dir.rstrip(os.sep) + "_archive"
             
        # shutil.make_archive adds the .zip extension automatically if format is zip
        # so strip .zip from the target path if the user included it
        if output_zip_path.endswith('.zip'):
             output_zip_path = output_zip_path[:-4]
             
        shutil.make_archive(output_zip_path, 'zip', source_dir)
        
        return f"Success! Directory '{source_dir}' has been heavily compressed.\nSaved ZIP to: {output_zip_path}.zip"
        
    except Exception as e:
         return f"Failed to compress directory: {e}"
