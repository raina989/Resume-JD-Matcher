# matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_cleaner import clean_text
import re

def enhanced_tfidf_match(resume_text, jd_text):
    """
    Fixed TF-IDF matching that won't return 0%
    """
    from text_cleaner import clean_text
    
    # Clean both texts
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)
    
    # Ensure we have enough text to work with
    if len(resume_clean.split()) < 5 or len(jd_clean.split()) < 5:
        return 0.5  # Baseline for very short texts
    
    try:
        # More lenient TF-IDF parameters
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 1),  # Use only unigrams for better matching
            max_df=0.99,  # Very high - include almost all words
            min_df=1,
            max_features=500,  # Reasonable feature limit
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=False
        )
        
        # Fit and transform
        vectors = vectorizer.fit_transform([resume_clean, jd_clean])
        
        # Check if we got any features
        if vectors.shape[1] == 0:
            # If no features, try without stop words
            vectorizer_no_stop = TfidfVectorizer(
                stop_words=None,  # No stop words removal
                ngram_range=(1, 1),
                max_df=1.0,
                min_df=1
            )
            vectors = vectorizer_no_stop.fit_transform([resume_clean, jd_clean])
            
            if vectors.shape[1] == 0:
                return 0.3  # Fallback score
        
        # Calculate similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Ensure minimum score
        similarity = max(0.1, similarity)  # At least 10%
        
        # Cap at reasonable maximum
        similarity = min(0.8, similarity)  # Not more than 80%
        
        return similarity
        
    except Exception as e:
        # Debug information (optional - remove in production)
        print(f"TF-IDF Debug: {str(e)[:100]}")
        return 0.3  # Reasonable fallback

def extract_experience_years(text):
    """
    Extract years of experience from text using multiple patterns
    """
    text_lower = text.lower()
    max_years = 0
    
    # Patterns for years of experience
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*in\s*\w+',
        r'(\d+)\s*-\s*(\d+)\s*years',
        r'(\d+)\s*years?\s*experience',
        r'(\d+)\s*years?\s*in',
        r'(\d+)\+?\s*years'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if isinstance(match, tuple):
                # Handle patterns that return tuples (like "2-5 years")
                for num in match:
                    if num and num.isdigit():
                        max_years = max(max_years, int(num))
            elif match.isdigit():
                max_years = max(max_years, int(match))
    
    # If no explicit years found, try to estimate from work history dates
    if max_years == 0:
        # Look for date ranges like "2020 - 2023"
        date_ranges = re.findall(r'(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}', text)
        if date_ranges:
            # Simple estimate: each range is at least 1 year
            max_years = len(date_ranges)
        
        # Also check for phrases like "over 5 years" or "5+ years"
        plus_patterns = [
            r'over\s+(\d+)\s*years',
            r'(\d+)\+\s*years',
            r'more\s+than\s+(\d+)\s*years'
        ]
        
        for pattern in plus_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match.isdigit():
                    max_years = max(max_years, int(match))
    
    return max_years

def calculate_match(resume_text, jd_text):
    """
    Simple TF-IDF matching (for backward compatibility)
    """
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([resume_clean, jd_clean])

    similarity_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity_score * 100, 2)

def calculate_detailed_match(resume_text, jd_text):
    """
    Comprehensive matching using multiple strategies with weighted scoring
    Returns both overall score and detailed breakdown
    """
    # Clean the texts
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)
    
    # Import here to avoid circular imports
    from skill_gap import extract_skills
    from keyword_gap import extract_keywords
    
    # ----- Strategy 1: TF-IDF Similarity (20% weight) -----
    tfidf_score = enhanced_tfidf_match(resume_text, jd_text)
    
    # ----- Strategy 2: Keyword Overlap Score (30% weight) -----
    resume_keywords = extract_keywords(resume_clean, top_n=30)
    jd_keywords = extract_keywords(jd_clean, top_n=30)
    
    if jd_keywords:
        keyword_overlap = len(resume_keywords & jd_keywords) / len(jd_keywords)
    else:
        keyword_overlap = 0
    
    # ----- Strategy 3: Skill Match Score (30% weight) -----
    resume_skills = extract_skills(resume_clean)
    jd_skills = extract_skills(jd_clean)
    
    if jd_skills:
        skill_match = len(resume_skills & jd_skills) / len(jd_skills)
    else:
        skill_match = 0
    
    # ----- Strategy 4: Experience Match (20% weight) -----
    resume_years = extract_experience_years(resume_text)
    jd_years = extract_experience_years(jd_text)
    
    if jd_years > 0:
        if resume_years >= jd_years:
            exp_score = 1.0  # Meets or exceeds requirement
        else:
            # Partial credit based on percentage of required years
            # Add 0.2 bonus for having some relevant experience
            exp_score = min(1.0, (resume_years / jd_years) + 0.2)
    else:
        exp_score = 1.0  # No experience requirement specified
    
    # ----- Calculate Weighted Score -----
    weights = {
        'tfidf': 0.20,      # TF-IDF similarity
        'keywords': 0.30,   # Keyword overlap
        'skills': 0.30,     # Skill match
        'experience': 0.20  # Experience match
    }
    
    weighted_score = (
        tfidf_score * weights['tfidf'] +
        keyword_overlap * weights['keywords'] +
        skill_match * weights['skills'] +
        exp_score * weights['experience']
    )
    
    # ----- Apply Bonuses for Meeting Basic Requirements -----
    bonus = 0
    
    # Bonus for having at least some required skills
    if skill_match > 0.3:  # Has at least 30% of required skills
        bonus += 0.1
    
    # Bonus for keyword coverage
    if keyword_overlap > 0.3:  # Has at least 30% of keywords
        bonus += 0.1
    
    # Bonus for having reasonable experience
    if jd_years > 0 and resume_years >= jd_years * 0.5:  # Has at least half the required experience
        bonus += 0.1
    
    # Calculate final score (capped at 100%)
    final_score = min(100, (weighted_score + bonus) * 100)
    
    # ----- Return Results -----
    return {
        'overall': round(final_score, 2),
        'breakdown': {
            'skills': round(skill_match * 100, 2),
            'keywords': round(keyword_overlap * 100, 2),
            'experience': round(exp_score * 100, 2),
            'tfidf': round(tfidf_score * 100, 2)
        },
        'details': {
            'resume_years': resume_years,
            'jd_years': jd_years,
            'resume_skills_count': len(resume_skills),
            'jd_skills_count': len(jd_skills),
            'matched_skills_count': len(resume_skills & jd_skills),
            'resume_keywords_count': len(resume_keywords),
            'jd_keywords_count': len(jd_keywords),
            'matched_keywords_count': len(resume_keywords & jd_keywords)
        }
    }

def get_match_interpretation(score):
    """
    Get a human-readable interpretation of the match score
    """
    if score >= 85:
        return {
            'level': 'EXCELLENT',
            'message': 'Your resume is exceptionally well-aligned with this position.',
            'action': 'You should definitely apply!'
        }
    elif score >= 70:
        return {
            'level': 'STRONG',
            'message': 'Your resume has strong alignment with the job requirements.',
            'action': 'Apply after making minor improvements.'
        }
    elif score >= 55:
        return {
            'level': 'GOOD',
            'message': 'Your resume shows good potential for this role.',
            'action': 'Make moderate improvements before applying.'
        }
    elif score >= 40:
        return {
            'level': 'MODERATE',
            'message': 'Your resume needs significant improvements for this role.',
            'action': 'Focus on adding missing skills and keywords.'
        }
    else:
        return {
            'level': 'WEAK',
            'message': 'This may not be the best fit with your current resume.',
            'action': 'Consider roles that better match your current skills.'
        }

# Test function (optional - can be removed in production)
if __name__ == "__main__":
    # Simple test with sample texts
    sample_resume = """
    Experienced Data Analyst with 3 years in business intelligence.
    Skills: Python, SQL, Data Visualization, Machine Learning.
    Developed predictive models and created comprehensive reports.
    """
    
    sample_jd = """
    Seeking Data Analyst with 2+ years experience.
    Required: SQL, Python, Data Analysis, Communication skills.
    Will develop systems and create documentation.
    """
    
    print("Testing matcher.py...")
    result = calculate_detailed_match(sample_resume, sample_jd)
    
    print(f"\nOverall Match: {result['overall']}%")
    print("\nBreakdown:")
    for category, score in result['breakdown'].items():
        print(f"  {category}: {score}%")
    
    interpretation = get_match_interpretation(result['overall'])
    print(f"\nInterpretation: {interpretation['level']}")
    print(f"Message: {interpretation['message']}")
    print(f"Action: {interpretation['action']}")