# src/keyword_gap.py - IMPROVED VERSION
from sklearn.feature_extraction.text import TfidfVectorizer
import re

def clean_for_keywords(text):
    """Simple text cleaning"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Fix spaces
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove special chars
    return text.strip()

def extract_keywords(text, top_n=15):
    """
    Extract important keywords from ANY text
    """
    cleaned = clean_for_keywords(text)
    
    # Get words
    words = cleaned.split()
    
    # Filter out common words
    common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'have', 'from'}
    filtered_words = [w for w in words if w not in common_words and len(w) > 3]
    
    if not filtered_words:
        # Fallback: return most frequent words
        from collections import Counter
        word_counts = Counter(words)
        return set([word for word, _ in word_counts.most_common(top_n)])
    
    # Use TF-IDF
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=50,
            ngram_range=(1, 2)
        )
        
        tfidf = vectorizer.fit_transform([cleaned])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf.toarray()[0]
        
        # Get top keywords
        scored = list(zip(feature_names, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        keywords = [word for word, score in scored[:top_n] if score > 0]
        
        # If not enough keywords, add frequent words
        if len(keywords) < top_n:
            from collections import Counter
            freq_words = [word for word, _ in Counter(filtered_words).most_common(top_n)]
            keywords.extend(freq_words[:top_n - len(keywords)])
        
        return set(keywords[:top_n])
        
    except:
        # Simple fallback
        from collections import Counter
        word_counts = Counter(filtered_words)
        return set([word for word, _ in word_counts.most_common(top_n)])