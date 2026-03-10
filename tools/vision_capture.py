import base64
import os

def load_image_as_base64(image_path: str) -> str:
    """Loads an image from the given path and returns it as a base64 encoded string.
    This is required for sending images to Ollama's vision models.
    
    Args:
        image_path: The absolute or relative path to the image file.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
        
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        raise Exception(f"Failed to load image: {str(e)}")
