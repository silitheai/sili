import base64

def encode_base64(text: str) -> str:
    """Encodes a standard string into base64 format."""
    try:
        encoded_bytes = base64.b64encode(text.encode('utf-8'))
        return f"Base64 Encoded: {encoded_bytes.decode('utf-8')}"
    except Exception as e:
        return f"Error encoding text: {str(e)}"
