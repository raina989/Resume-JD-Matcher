# industry_detector.py
def detect_industry(jd_text):
    """Detect industry from job description"""
    jd_lower = jd_text.lower()
    
    industry_keywords = {
        'tech': ['software', 'technology', 'it', 'developer', 'engineer', 'programming'],
        'finance': ['finance', 'banking', 'investment', 'accounting', 'financial'],
        'healthcare': ['healthcare', 'medical', 'pharmaceutical', 'hospital', 'clinical'],
        'education': ['education', 'teaching', 'academic', 'university', 'school'],
        'retail': ['retail', 'ecommerce', 'merchandising', 'customer service'],
        'marketing': ['marketing', 'advertising', 'brand', 'digital marketing', 'pr'],
    }
    
    for industry, keywords in industry_keywords.items():
        if any(keyword in jd_lower for keyword in keywords):
            return industry
    
    return 'general'