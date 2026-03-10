import re

def analyze_sentiment(text: str) -> str:
    """Performs a basic, zero-dependency local NLP sentiment analysis (Positive, Negative, Neutral) on a block of text."""
    try:
        # Since we want to keep it lightweight (no NLTK/Spacy dependency blob), we use a rough lexicon keyword approach
        positive_words = {"good", "great", "excellent", "amazing", "love", "happy", "joy", "success", "win", "awesome", "fantastic", "brilliant", "perfect"}
        negative_words = {"bad", "terrible", "awful", "hate", "sad", "fail", "lose", "angry", "worst", "horrible", "stupid", "disaster", "pain"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return "Cannot analyze sentiment of empty or non-alphabetical text."
            
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        
        total_valence = pos_count + neg_count
        
        if total_valence == 0:
            sentiment = "NEUTRAL"
            confidence = 0.0
        else:
            if pos_count > neg_count:
                sentiment = "POSITIVE"
                confidence = (pos_count / total_valence) * 100
            elif neg_count > pos_count:
                sentiment = "NEGATIVE"
                confidence = (neg_count / total_valence) * 100
            else:
                sentiment = "NEUTRAL (Mixed)"
                confidence = 50.0
                
        output = f"--- ZERO-DEP SENTIMENT ANALYSIS ---\n"
        output += f"Overall Sentiment: {sentiment}\n"
        output += f"Confidence Score: {confidence:.1f}%\n"
        output += f"(Keywords Detected: {pos_count} Positive | {neg_count} Negative)\n"
        
        return output
    except Exception as e:
        return f"Sentiment analysis failed: {e}"
