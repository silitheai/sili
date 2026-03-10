import base64

def decode_base64(encoded_text: str) -> str:
    """Decodes a base64 string back into standard text."""
    try:
        decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
        return f"Decoded Text: {decoded_bytes.decode('utf-8')}"
    except Exception as e:
        return f"Error decoding base64: {str(e)}"
