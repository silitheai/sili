import csv
import json
import os

def csv_to_json(csv_file_path: str, output_file_path: str = None) -> str:
    """Reads a CSV file from disk, parses it into JSON, and optionally writes it to a new file."""
    if not os.path.exists(csv_file_path):
        return f"Error: CSV file '{csv_file_path}' not found."
        
    try:
        data = []
        with open(csv_file_path, 'r', encoding='utf-8') as csvf:
             csv_reader = csv.DictReader(csvf)
             for row in csv_reader:
                 data.append(row)
                 
        if not data:
             return "CSV was parsed but appears to be empty."
             
        json_string = json.dumps(data, indent=4)
        
        if output_file_path:
             with open(output_file_path, 'w', encoding='utf-8') as jsonf:
                  jsonf.write(json_string)
             return f"Successfully converted CSV to JSON and saved to {output_file_path}."
             
        # If no output path, return the raw string (truncated)
        if len(json_string) > 10000:
             json_string = json_string[:10000] + "\n... [TRUNCATED] ..."
             
        return f"--- JSON OUTPUT ---\n{json_string}"
    except Exception as e:
        return f"Failed to convert CSV to JSON format: {str(e)}"
