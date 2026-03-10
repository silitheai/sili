import secrets
import string

def generate_password(length: int = 16) -> str:
    """Generates a highly secure random password of the specified length."""
    if length < 8:
        return "Error: Password length should be at least 8 characters for security."
        
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"Generated Secure Password: {password}"
