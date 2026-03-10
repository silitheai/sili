import os

def visualize_directory(startpath: str = '.', depth: int = 2) -> str:
    """Generates a visual tree structure of a directory and its contents up to a specified depth."""
    if not os.path.exists(startpath):
        return f"Error: Directory '{startpath}' does not exist on disk."
        
    start_level = startpath.rstrip(os.sep).count(os.sep)
    output = f"DIRECTORY TREE FOR '{startpath}' (Max Depth: {depth})\n"
    output += "=================================================\n"
    
    file_count = 0
    dir_count = 0
    
    try:
        for root, dirs, files in os.walk(startpath):
            level = root.rstrip(os.sep).count(os.sep) - start_level
            if level > depth:
                continue
                
            indent = '    ' * level
            output += f"{indent}📁 {os.path.basename(root)}/\n"
            subindent = '    ' * (level + 1)
            
            # Don't go deep down inside virtual environments or massive dists automatically
            if os.path.basename(root) in ['.git', 'node_modules', 'venv', '__pycache__']:
                 dirs.clear() # Stop walking this branch
                 output += f"{subindent}... [Contents hidden for cleanliness]\n"
                 continue
                 
            for f in files:
                output += f"{subindent}📄 {f}\n"
                file_count += 1
                
            dir_count += len(dirs)
            
            # Prevents context explosion
            if len(output) > 20000:
                output += f"\n... [TREE TRUNCATED (Too large)]"
                break
                
        output += f"\nTotal visible count: {dir_count} directories, {file_count} files."
        return output
    except Exception as e:
        return f"Failed to generate tree view: {e}"
