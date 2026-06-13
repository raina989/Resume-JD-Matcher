# src/keyword_gap.py
import re
from collections import Counter

# Common English stopwords (balanced - not too aggressive)
STOPWORDS = {
    'a', 'a', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
    'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was',
    'were', 'will', 'with', 'i', 'you', 'we', 'they', 'our', 'your', 'their',
    'this', 'that', 'these', 'those', 'am', 'do', 'does', 'did', 'doing',
    'have', 'having', 'but', 'or', 'yet', 'so', 'such', 'both', 'each',
    'either', 'neither', 'every', 'all', 'any', 'no', 'none', 'some', 'few',
    'many', 'much', 'most', 'other', 'same', 'only', 'own', 'than', 'then',
    'thence', 'there', 'through', 'throughout', 'thru', 'until', 'up', 'upon',
    'without', 'after', 'before', 'above', 'below', 'between', 'using', 'use'
}

# Industry-agnostic business terms (expanded but not overly restrictive)
BUSINESS_TERMS = {
    # Leadership & Management
    'lead', 'manage', 'strategy', 'strategic', 'planning', 'execution',
    'leadership', 'management', 'supervision', 'coordination', 'oversight',
    
    # Communication & Soft Skills
    'communication', 'collaboration', 'negotiation', 'presentation',
    'interpersonal', 'teamwork', 'relationship', 'stakeholder', 'client',
    
    # Analysis & Problem Solving
    'analysis', 'analytical', 'problem', 'solving', 'critical', 'thinking',
    'research', 'evaluation', 'assessment', 'optimization', 'improvement',
    
    # Project & Process
    'project', 'program', 'agile', 'scrum', 'process', 'workflow', 'timeline',
    'milestone', 'deliverable', 'budget', 'resource',
    
    # Technical
    'technical', 'digital', 'software', 'system', 'platform', 'data',
    'analytics', 'reporting', 'dashboard', 'metrics', 'kpi',
    
    # Financial
    'financial', 'budget', 'forecast', 'revenue', 'profit', 'cost', 'roi',
    'growth', 'scalable', 'efficiency', 'productivity',
    
    # Sales & Marketing
    'sales', 'marketing', 'advertising', 'brand', 'awareness', 'acquisition',
    'retention', 'engagement', 'conversion', 'campaign', 'content', 'social',
    
    # HR
    'recruiting', 'hiring', 'onboarding', 'training', 'development',
    'performance', 'feedback', 'compensation',
    
    # Healthcare
    'patient', 'clinical', 'medical', 'healthcare', 'diagnosis', 'treatment',
    
    # Legal
    'legal', 'compliance', 'regulatory', 'contract', 'litigation',
    
    # Education
    'education', 'teaching', 'curriculum', 'instruction', 'student',
    
    # Engineering
    'engineering', 'design', 'development', 'testing', 'quality', 'manufacturing',
    
    # Action Verbs
    'develop', 'create', 'design', 'implement', 'execute', 'deliver',
    'achieve', 'improve', 'increase', 'decrease', 'reduce', 'enhance',
    'optimize', 'streamline', 'transform', 'drive', 'support', 'coordinate'
}

# Synonym mapping for better matching
SYNONYMS = {
    'execute scalable': ['scalable growth', 'scaling', 'growth strategies', 'scale'],
    'performance metrics': ['kpi', 'metrics', 'performance', 'dashboard', 'analytics', 'campaign metrics'],
    'brand awareness': ['brand', 'awareness', 'visibility', 'qualified leads', 'recognition'],
    'advertising platforms': ['google ads', 'meta', 'facebook ads', 'paid social', 'ad platform'],
    'campaign performance': ['campaign', 'performance', 'roas', 'results', 'campaign metrics'],
    'scalable growth': ['scaling', 'growth', 'expand', 'scale up', 'growth strategies'],
    'maximizing roi': ['roi', 'return', 'investment', 'profitability', 'high-roi'],
    'customer acquisition': ['acquisition', 'customer', 'lead generation', 'cac', 'acquiring customers'],
    'team leadership': ['lead', 'manage', 'mentor', 'supervise', 'leadership', 'managing team'],
    'budget management': ['budget', 'financial', 'cost', 'spend', 'expense', 'budget optimization'],
    'data analytics': ['data', 'analytics', 'analysis', 'insights', 'metrics', 'ga4'],
    'project management': ['project', 'manage', 'deliver', 'timeline', 'milestone']

    #healthcare

    #finance

    #engineering

}

def extract_keywords(text, top_n=40):
    """Extract clean, meaningful keywords from text"""
    if not text:
        return set()
    
    # Clean text
    try:
        from text_cleaner import clean_text_for_keywords
        text = clean_text_for_keywords(text)
    except:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
    
    words = text.split()
    
    if len(words) < 3:
        return set()
    
    keywords = {}
    
    # Extract 2-word phrases (INCREASED WEIGHT)
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i+1]
        
        # Skip only essential stopwords
        if word1 in STOPWORDS or word2 in STOPWORDS:
            continue
        
        if len(word1) < 2 or len(word2) < 2:  # Allow 2-letter words (like "roi", "seo")
            continue
        
        phrase = f"{word1} {word2}"
        
        # Skip obvious garbage
        if is_garbage_phrase(phrase):
            continue
        
        # Give higher weight to business terms
        if any(term in phrase.lower() for term in BUSINESS_TERMS):
            keywords[phrase] = keywords.get(phrase, 0) + 3
        else:
            keywords[phrase] = keywords.get(phrase, 0) + 2
    
    # Extract important single words
    for word in words:
        if (len(word) > 2 and  # Allow 3+ letter words
            word not in STOPWORDS and 
            not word.isdigit()):
            
            if word in BUSINESS_TERMS:
                keywords[word] = keywords.get(word, 0) + 2
            else:
                keywords[word] = keywords.get(word, 0) + 1
    
    # Sort and return top N (INCREASED from 30 to 40)
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    result = {kw for kw, score in sorted_keywords[:top_n]}
    
    return result

def is_garbage_phrase(phrase):
    """Check if a phrase is definitely garbage (minimal filtering)"""
    garbage_phrases = [
        'we are', 'we are seeking', 'type full', 'full time', 'part time',
        'ideal candidate', 'candidate possesses', 'qualified candidate',
        'successful candidate', 'about us', 'why join', 'reports to',
        'position summary', 'time position', 'job title', 'department location'
    ]
    
    phrase_lower = phrase.lower()
    for garbage in garbage_phrases:
        if garbage in phrase_lower:
            return True
    
    # Don't filter by length or other metrics - keep more keywords
    return False

def match_keywords_with_context(resume_keywords, jd_keywords, resume_text, jd_text):
    """Match JD keywords against resume keywords (lenient for higher match rate)"""
    matched = []
    missing = []
    partial_matches = {}
    semantic_matches = {}
    
    resume_text_lower = resume_text.lower()
    resume_keywords_lower = {kw.lower() for kw in resume_keywords}
    
    for jd_kw in jd_keywords:
        jd_kw_lower = jd_kw.lower()
        
        # Skip obvious garbage only
        if len(jd_kw) < 3 or jd_kw.lower() in ['candidate', 'ideal', 'title']:
            continue
        
        # Check 1: Exact match
        if jd_kw_lower in resume_keywords_lower:
            matched.append(jd_kw)
            continue
        
        # Check 2: Substring match (lenient)
        found = False
        for rk in resume_keywords:
            rk_lower = rk.lower()
            if (jd_kw_lower in rk_lower or rk_lower in jd_kw_lower):
                matched.append(jd_kw)
                partial_matches[jd_kw] = rk
                found = True
                break
        
        if found:
            continue
        
        # Check 3: Synonym matching
        found_synonym = False
        if jd_kw_lower in SYNONYMS:
            for synonym in SYNONYMS[jd_kw_lower]:
                if synonym in resume_text_lower or any(synonym in rk.lower() for rk in resume_keywords):
                    matched.append(jd_kw)
                    semantic_matches[jd_kw] = f"synonym: {synonym}"
                    found_synonym = True
                    break
        
        if found_synonym:
            continue
        
        # Check 4: Word overlap (lenient - any word match)
        jd_words = set(jd_kw_lower.split())
        for rk in resume_keywords:
            rk_words = set(rk.lower().split())
            if len(jd_words & rk_words) >= 1:
                matched.append(jd_kw)
                partial_matches[jd_kw] = f"{rk} (word match)"
                found = True
                break
        
        if found:
            continue
        
        # Check 5: Check if ANY part appears in resume text
        if jd_kw_lower in resume_text_lower:
            matched.append(jd_kw)
            partial_matches[jd_kw] = "found in resume text"
            continue
        
        # Only mark as missing if it's a meaningful term
        if len(jd_kw) > 3 and not is_garbage_phrase(jd_kw):
            missing.append(jd_kw)
    
    # Calculate match percentage based on total JD keywords
    total_jd_keywords = len([kw for kw in jd_keywords if len(kw) > 3 and not is_garbage_phrase(kw)])
    match_score = (len(matched) / total_jd_keywords * 100) if total_jd_keywords > 0 else 0
    
    return {
        'matched': matched,
        'missing': missing[:10],
        'partial_matches': partial_matches,
        'semantic_matches': semantic_matches,
        'match_percentage': match_score
    }

def get_word_stems(word):
    """Extract word stems for fuzzy matching"""
    stems = set()
    
    endings = ['ing', 'ed', 'er', 'or', 'ion', 'tion', 's', 'es', 
               'ment', 'ance', 'ence', 'ive', 'ative', 'ize', 'ise']
    
    for ending in endings:
        if word.endswith(ending):
            stem = word[:-len(ending)]
            if len(stem) > 3:
                stems.add(stem)
    
    stems.add(word)
    
    # Handle plurals
    if word.endswith('s') and not word.endswith('ss'):
        stems.add(word[:-1])
    if not word.endswith('s') and len(word) > 3:
        stems.add(word + 's')
    
    return stems

def extract_phrases_from_text(text, min_freq=1):
    """Extract common phrases from text for suggestions"""
    if not text:
        return []
    
    try:
        from text_cleaner import clean_text_for_keywords
        text = clean_text_for_keywords(text)
    except:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
    
    words = text.split()
    phrases = []
    
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i+1]
        
        if word1 in STOPWORDS or word2 in STOPWORDS:
            continue
        if len(word1) < 2 or len(word2) < 2:
            continue
        
        phrase = f"{word1} {word2}"
        
        if not is_garbage_phrase(phrase):
            phrases.append(phrase)
    
    phrase_counts = Counter(phrases)
    
    result = []
    for phrase, count in phrase_counts.most_common(20):
        if count >= min_freq:
            result.append(phrase)
    
    return result[:15]