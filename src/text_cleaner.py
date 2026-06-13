# src/text_cleaner.py
import re

def clean_text(text):
    """
    Clean text by removing garbage, fixing formatting, and preparing for analysis
    """
    if not text:
        return ""
    
    # Remove common PDF/OCR garbage
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
    text = re.sub(r'\x00', ' ', text)  # Remove null bytes
    
    # Remove common garbage patterns
    text = re.sub(r'[•·●■◆▪►○●□]', ' ', text)  # Remove bullets
    text = re.sub(r'[\|\/\\]', ' ', text)  # Remove separators
    
    # Fix line breaks
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    
    # Remove standalone single characters (but keep "a" and "i" in context)
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
    
    # Remove words that are just numbers
    text = re.sub(r'\s+\d+\s+', ' ', text)
    
    # Fix common concatenated words
    text = re.sub(r'(\w+)(time)(\w+)', r'\1 \2 \3', text)
    text = re.sub(r'(\w+)(summary)(\w+)', r'\1 \2 \3', text)
    text = re.sub(r'(\w+)(position)(\w+)', r'\1 \2 \3', text)
    text = re.sub(r'(\w+)(manager)(\w+)', r'\1 \2 \3', text)
    text = re.sub(r'(\w+)(location)(\w+)', r'\1 \2 \3', text)
    text = re.sub(r'(\w+)(department)(\w+)', r'\1 \2 \3', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing spaces
    text = text.strip()
    
    # Fix sentence boundaries
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Lowercase for consistency
    text = text.lower()
    
    return text

def clean_text_for_keywords(text):
    """
    Extra cleaning specifically for keyword extraction
    """
    text = clean_text(text)
    
    # Remove job posting boilerplate phrases
    boilerplate = [
        'we are seeking', 'we are looking for', 'we are hiring', 
        'ideal candidate', 'candidate should have', 'candidate must have',
        'candidate possesses', 'qualified candidate', 'successful candidate',
        'responsible for', 'duties include', 'key responsibilities',
        'requirements include', 'qualifications include', 'about us',
        'why join us', 'what we offer', 'benefits include', 'perks include',
        'job title', 'position type', 'employment type', 'work location',
        'reports to', 'directly report', 'team member', 'cross functional'
    ]
    
    for phrase in boilerplate:
        text = re.sub(r'\b' + phrase + r'\b', '', text, flags=re.IGNORECASE)
    
    # Remove common words that appear at start of lines
    garbage_starts = ['summary', 'position summary', 'type', 'full time', 
                      'full time position', 'location', 'department']
    
    for garbage in garbage_starts:
        text = re.sub(r'^' + garbage + r'\s+', '', text, flags=re.MULTILINE)
    
    # Remove standalone words that are likely garbage
    garbage_words = ['summarywe', 'timeposition', 'positionwe', 'weare', 'areyou',
                     'positiontype', 'typedepartment', 'departmentlocation',
                     'candidate', 'ideal', 'possesses', 'qualifications']
    
    for word in garbage_words:
        text = text.replace(word, '')
    
    # Remove any remaining weird characters
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short words (less than 3 chars) that might be leftover garbage
    text = ' '.join([w for w in text.split() if len(w) >= 3])
    
    return text