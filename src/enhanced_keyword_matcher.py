# src/enhanced_keyword_matcher.py
"""
ULTRA-SIMPLIFIED BUT HIGHLY EFFECTIVE KEYWORD MATCHER
No complex dependencies - just works!
"""

import re
from collections import Counter

# Common English stopwords to ignore
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
    'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was',
    'were', 'will', 'with', 'i', 'you', 'we', 'they', 'our', 'your', 'their',
    'this', 'that', 'these', 'those', 'am', 'do', 'does', 'did', 'doing',
    'have', 'having', 'the', 'and', 'for', 'but', 'or', 'yet', 'so', 'such',
    'both', 'each', 'either', 'neither', 'every', 'all', 'any', 'no', 'none',
    'some', 'few', 'many', 'much', 'most', 'other', 'same', 'only', 'own',
    'same', 'than', 'then', 'thence', 'there', 'these', 'they', 'this',
    'those', 'through', 'throughout', 'thru', 'until', 'up', 'upon', 'with',
    'without', 'after', 'before', 'above', 'below', 'between', 'using', 'use'
}

def extract_keywords_improved(text, top_n=30):
    """
    Extract keywords with emphasis on PHRASES (2-3 word combinations)
    This is what you've been missing!
    """
    # Clean text
    text = text.lower()
    text = re.sub(r'[^\w\s\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    words = text.split()
    
    # Extract different types of keywords
    keywords = {}
    
    # 1. PHRASES (most important - 2-3 word combinations)
    # This solves the "customer acquisition" problem!
    for i in range(len(words) - 1):
        # 2-word phrases
        if i + 1 < len(words):
            phrase2 = f"{words[i]} {words[i+1]}"
            if not any(word in STOPWORDS for word in phrase2.split()[:2]):
                keywords[phrase2] = keywords.get(phrase2, 0) + 2  # Higher weight
        
        # 3-word phrases  
        if i + 2 < len(words):
            phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}"
            # Only keep if it's likely meaningful (not full of stopwords)
            phrase_words = phrase3.split()
            stopword_count = sum(1 for w in phrase_words if w in STOPWORDS)
            if stopword_count <= 1:  # At most 1 stopword
                keywords[phrase3] = keywords.get(phrase3, 0) + 3  # Even higher weight
    
    # 2. Important single words (not stopwords, not too short)
    for word in words:
        if (len(word) > 2 and 
            word not in STOPWORDS and 
            not word.isdigit() and
            not any(c.isdigit() for c in word)):
            keywords[word] = keywords.get(word, 0) + 1
    
    # 3. Technical/business terms get boosted
    boost_terms = ['marketing', 'sales', 'digital', 'seo', 'sem', 'analytics', 
                   'data', 'acquisition', 'retention', 'strategy', 'management',
                   'development', 'python', 'java', 'javascript', 'react', 'aws',
                   'lead', 'customer', 'business', 'product', 'project']
    
    for term in boost_terms:
        if term in keywords:
            keywords[term] = keywords[term] * 1.5
    
    # Sort by frequency/importance and return top N
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    return set([kw for kw, score in sorted_keywords[:top_n]])


def match_keywords_intelligently(resume_keywords, jd_keywords, resume_text, jd_text):
    """
    Match keywords with intelligence:
    - Exact matches
    - Substring matches (partial)
    - Semantic word matches (same root word)
    """
    matched = []
    missing = []
    partial_info = {}
    
    resume_text_lower = resume_text.lower()
    
    for jd_kw in jd_keywords:
        jd_kw_lower = jd_kw.lower()
        found = False
        
        # Check 1: Exact match
        if jd_kw_lower in resume_keywords:
            matched.append(jd_kw)
            continue
        
        # Check 2: Substring match (e.g., "manage" in "management")
        for rk in resume_keywords:
            if (jd_kw_lower in rk or rk in jd_kw_lower) and len(jd_kw_lower) > 3:
                matched.append(jd_kw)
                partial_info[jd_kw] = rk
                found = True
                break
        
        if found:
            continue
        
        # Check 3: Word stem matching (e.g., "manage" matches "manager", "management")
        jd_stems = get_word_stems(jd_kw_lower)
        for rk in resume_keywords:
            rk_stems = get_word_stems(rk)
            if jd_stems & rk_stems:  # If they share stems
                matched.append(jd_kw)
                partial_info[jd_kw] = f"{rk} (stem match)"
                found = True
                break
        
        if found:
            continue
        
        # Check 4: Check if keyword appears as part of a phrase in resume
        if jd_kw_lower in resume_text_lower:
            matched.append(jd_kw)
            partial_info[jd_kw] = "found in text but not as keyword"
            continue
        
        # If all checks fail, it's missing
        missing.append(jd_kw)
    
    match_score = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0
    
    return {
        'matched': matched,
        'missing': missing,
        'partial_info': partial_info,
        'match_percentage': match_score
    }


def get_word_stems(word):
    """Get common stems/roots of a word for fuzzy matching"""
    stems = set()
    
    # Remove common endings
    endings = ['ing', 'ed', 'er', 'or', 'ion', 'tion', 's', 'es', 'ment', 'ance', 'ence']
    for ending in endings:
        if word.endswith(ending):
            stem = word[:-len(ending)]
            if len(stem) > 3:
                stems.add(stem)
    
    stems.add(word)  # Always include original
    
    # Add plural/singular variations
    if word.endswith('s') and not word.endswith('ss'):
        stems.add(word[:-1])
    if not word.endswith('s') and len(word) > 3:
        stems.add(word + 's')
    
    return stems


def extract_phrases_simple(text, min_freq=1):
    """Simple but effective phrase extraction"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    
    phrases = []
    for i in range(len(words) - 1):
        # 2-word phrases
        phrase2 = f"{words[i]} {words[i+1]}"
        # Filter out phrases with stopwords
        if not any(w in STOPWORDS for w in [words[i], words[i+1]]):
            phrases.append(phrase2)
        
        # 3-word phrases
        if i + 2 < len(words):
            phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}"
            if not any(w in STOPWORDS for w in phrase3.split()[:2]):
                phrases.append(phrase3)
    
    # Count frequencies
    phrase_counts = Counter(phrases)
    
    # Return only phrases that appear multiple times or are business-critical
    result = []
    for phrase, count in phrase_counts.most_common(30):
        if count >= min_freq:
            # Check if it's a meaningful business/technical phrase
            business_terms = ['marketing', 'sales', 'customer', 'acquisition', 
                            'strategy', 'management', 'development', 'analysis']
            if any(term in phrase for term in business_terms) or count >= 2:
                result.append(phrase)
    
    return result