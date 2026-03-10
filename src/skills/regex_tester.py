import re

def regex_tester(pattern: str, target_text: str) -> str:
    """Safely executes a regular expression against target text, returning all matches and groups."""
    try:
        # Prevent pathological complexity explosions by not using massive text blocks
        if len(target_text) > 10000:
             target_text = target_text[:10000]
             
        matches = list(re.finditer(pattern, target_text))
        
        if not matches:
             return f"No matches found in the target string for pattern `{pattern}`."
             
        output = f"REGEX EVALUATION for `{pattern}`\n"
        output += f"Total Matches Found: {len(matches)}\n"
        output += "-" * 30 + "\n"
        
        limit = min(50, len(matches))
        for i, match in enumerate(matches[:limit], 1):
             output += f"[Match {i}] Range: {match.span()}\n"
             output += f"Value: '{match.group()}'\n"
             
             # Show capture groups if there are any
             if match.groups():
                  output += "Groups: " + ", ".join([f"({j+1}) '{g}'" for j, g in enumerate(match.groups())]) + "\n"
             output += "\n"
             
        if len(matches) > 50:
             output += "... [Truncated extra matches]"
             
        return output
    except re.error as e:
         return f"REGEX SYNTAX ERROR in '{pattern}':\nDetails: {e}"
    except Exception as e:
         return f"Failed to evaluate regex: {e}"
