import re

def count_tokens(text: str) -> str:
    """Estimates the number of LLM tokens in a given string using a rough ~4 characters per token heuristic."""
    if not text:
        return "Given text was empty. 0 Tokens."
        
    try:
        # A rough heuristic: 1 token ~= 4 chars in English, or roughly 0.75 of a word
        char_count = len(text)
        word_count = len(text.split())
        
        # A simple estimation blending words and chars
        token_estimate_chars = char_count / 4.0
        token_estimate_words = word_count / 0.75
        
        final_estimate = int((token_estimate_chars + token_estimate_words) / 2)
        
        output = f"--- LLM TOKEN ESTIMATION ---\n"
        output += f"Characters: {char_count:,}\n"
        output += f"Words: {word_count:,}\n"
        output += f"Estimated Tokens (Llama/GPT context size): ~{final_estimate:,}\n"
        
        # Add basic warnings for local 8k windows
        if final_estimate > 8000:
             output += "\n⚠️ WARNING: This text exceeds 8,000 tokens and may overflow standard local context windows!"
             
        return output
    except Exception as e:
        return f"Failed to estimate token limit: {e}"
