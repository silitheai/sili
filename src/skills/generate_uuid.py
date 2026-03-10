import uuid

def generate_uuid(count: int = 1) -> str:
    """Generates one or more extremely secure, random UUIDv4 strings."""
    try:
        count = min(count, 500) # Prevents context flooding
        
        if count <= 1:
            return f"{uuid.uuid4()}"
            
        output = f"--- GENERATING {count} SECURE UUIDs ---\n"
        for i in range(count):
            output += f"{i+1}. {uuid.uuid4()}\n"
            
        return output
    except Exception as e:
        return f"Failed to generate UUID strings: {e}"
