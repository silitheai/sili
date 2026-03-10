import urllib.parse

def generate_qr_code(data: str) -> str:
    """Generates a QR code for the provided text/URL and returns a direct image link."""
    # Using the free api.qrserver.com service 
    # to avoid needing the Pillow/qrcode pip installations 
    try:
        encoded_data = urllib.parse.quote(data)
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_data}"
        return f"Success. You can view or download the QR Code here: {url}"
    except Exception as e:
        return f"Error generating QR code link: {str(e)}"
