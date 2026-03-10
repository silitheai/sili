import requests
import json

def ollama_status():
    """
    Fetches the current status of the local Ollama instance.
    Returns a list of downloaded models and connectivity details.
    """
    try:
        # Check tags API for available models
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if not models:
                return "Ollama is running but no models are downloaded. Run 'ollama pull llama3' to get started."
            
            # Format model list
            model_list = []
            for m in models:
                size_gb = round(m.get('size', 0) / (1024**3), 2)
                model_list.append(f"• {m['name']} ({size_gb} GB)")
            
            status_text = "✅ **Ollama Status: Online**\n\n"
            status_text += "**Downloaded Models:**\n" + "\n".join(model_list)
            status_text += "\n\nSili is currently synchronized with these local neural weights."
            return status_text
        else:
            return f"❌ Ollama returned status code {response.status_code}. Is the service running?"
    except requests.exceptions.ConnectionError:
        return "❌ **Ollama Status: Offline**\n\nSili cannot reach localhost:11434. Please ensure Ollama is installed and running."
    except Exception as e:
        return f"❌ Error checking Ollama: {str(e)}"
