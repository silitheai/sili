import json
import csv
import io

def generate_markdown_table(data_string: str) -> str:
    """Detects raw JSON or CSV text payloads and dynamically generates a beautifully formatted Markdown table string."""
    try:
         # Try JSON parsing first
         parsed_data = None
         try:
              parsed_data = json.loads(data_string)
         except json.JSONDecodeError:
              pass
              
         if parsed_data and isinstance(parsed_data, list) and len(parsed_data) > 0 and isinstance(parsed_data[0], dict):
              # It's a JSON array of objects
              headers = list(parsed_data[0].keys())
              rows = [[str(row.get(h, '')) for h in headers] for row in parsed_data]
         else:
              # Try CSV parsing
              f = io.StringIO(data_string.strip())
              reader = csv.reader(f)
              rows_data = list(reader)
              
              if not rows_data or len(rows_data) < 2:
                  return "Error: Could not parse input as a meaningful JSON array of objects or multi-line CSV format."
              headers = rows_data[0]
              rows = rows_data[1:]
              
         # Build Markdown
         # Prevent context blowup
         rows = rows[:50]
         
         # Max column width calculation for aesthetics
         col_widths = [len(str(h)) for h in headers]
         for row in rows:
             for i, val in enumerate(row):
                 if i < len(col_widths):
                     col_widths[i] = max(col_widths[i], len(str(val)))
                     
         # Generate Header
         md_table = "| " + " | ".join([str(h).ljust(w) for h, w in zip(headers, col_widths)]) + " |\n"
         
         # Generate Separator
         md_table += "|" + "|".join(["-" * (w + 2) for w in col_widths]) + "|\n"
         
         # Generate Rows
         for row in rows:
             # Handle missing columns gracefully
             padded_row = [str(val).ljust(w) for val, w in zip(row + [''] * (len(headers) - len(row)), col_widths)]
             md_table += "| " + " | ".join(padded_row) + " |\n"
             
         return md_table
         
    except Exception as e:
         return f"Failed to generate Markdown table: {e}"
