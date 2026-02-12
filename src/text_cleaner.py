# text_cleaner.py - Improved
import re

def clean_text(text):
    """
    Comprehensive text cleaning for matching algorithms
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '', text)
    
    # Replace newlines, tabs, multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', ' ', text)
    
    # Remove standalone single letters
    text = re.sub(r'\b[a-z]\b', '', text)
    
    # Remove extra whitespace
    text = text.strip()
    
    return text