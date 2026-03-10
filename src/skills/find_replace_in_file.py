import os
import re

def find_replace_in_file(file_path: str, find_pattern: str, replace_text: str, is_regex: bool = False) -> str:
    """Scans an entire local file and replaces text based on an exact string or a Regular Expression."""
    if not os.path.exists(file_path):
        return f"Error: Target file '{file_path}' does not exist."
        
    try:
        # Quick safety net on self-modification while it runs
        if "vector_memory" in file_path or ".sqlite" in file_path.lower():
             return "CRITICAL ERROR: Cannot string-replace inside raw SQLite vectors. Use SQL logic!"
             
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
             original_content = f.read()
             
        if is_regex:
             # Apply regex rules
             try:
                  new_content, count = re.subn(find_pattern, replace_text, original_content)
             except re.error as e:
                  return f"REGEX SYNTAX ERROR in your find pattern:\nDetails: {e}"
        else:
             # Exact match
             count = original_content.count(find_pattern)
             new_content = original_content.replace(find_pattern, replace_text)
             
        if count == 0:
             return f"No occurrences of '{find_pattern}' found in '{file_path}'. File remains unchanged."
             
        # Commit write disk
        with open(file_path, 'w', encoding='utf-8') as f:
             f.write(new_content)
             
        return f"FIND & REPLACE COMPLETE!\nReplaced {count} instances in '{file_path}' successfully."
        
    except Exception as e:
         return f"Failed to execute mass textual replacement on {file_path}:\n{e}"
