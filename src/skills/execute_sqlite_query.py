import sqlite3
import os

def execute_sqlite_query(db_path: str, query: str) -> str:
    """Executes a RAW SQL query directly against a local SQLite database file and prints the fetched results."""
    # Basic existence verification
    if not os.path.exists(db_path):
         return f"Error: Database file not found at {db_path}."
         
    # Safety Check: Do not allow destruction of the agent's core memory
    if "vector_store" in db_path or "memory" in db_path:
        return "CRITICAL ERROR: Refusing to execute raw modifications against Sili's core database memory vectors."
        
    try:
        # Read-Write execution
        conn = sqlite3.connect(db_path)
        
        # Enforce dict style rows for better string representation
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Run the command
        cursor.execute(query)
        
        # Auto-commit if it's an Insert/Update/Delete pattern
        action_word = query.strip().split()[0].upper()
        if action_word in ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]:
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            return f"Query executed successfully. Rows affected: {rows_affected}"
            
        # If it's a SELECT, fetch data
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
             return "Query executed successfully, but returned 0 rows."
             
        # Format output
        output = f"--- QUERY RESULTS (Total Rows: {len(rows)}) ---\n"
        
        # Limit rows to prevent massive hallucinations
        limit = min(50, len(rows))
        
        for i in range(limit):
             row_dict = dict(rows[i])
             output += f"Row {i+1}: {row_dict}\n"
             
        if len(rows) > 50:
             output += f"\n... [Truncated {len(rows) - 50} additional rows]"
             
        return output
        
    except sqlite3.Error as e:
         return f"SQLite Execution Error: {e}"
    except Exception as e:
         return f"Error connecting to database: {e}"
