# src/matcher.py
import re
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Local module imports
from text_cleaner import clean_text
from skill_gap import extract_skills
from keyword_gap import extract_keywords, match_keywords_with_context, extract_phrases_from_text

# =====================================================
# LOAD SEMANTIC MODEL
# =====================================================

@st.cache_resource
def get_model():
    """Loads and caches the model so it only downloads once."""
    return SentenceTransformer("all-MiniLM-L6-v2")

# =====================================================
# EXPERIENCE EXTRACTION
# =====================================================

def extract_experience_years(text):
    """Extract years of experience from text"""
    text = text.lower()
    years = []

    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'(\d+)\+?\s*years',
        r'over\s+(\d+)\s*years',
        r'more than\s+(\d+)\s*years',
        r'(\d+)\s*\+\s*years',
        r'experience\s*:\s*(\d+)\+?\s*years',
        r'(\d+)-(\d+)\s*years',
        r'(\d+)\s+years'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    years.append(int(match[-1]))
                else:
                    years.append(int(match))
            except:
                pass

    return max(years) if years else 0

# =====================================================
# SEMANTIC SIMILARITY
# =====================================================

def calculate_similarity(resume_text, jd_text):
    """Calculate semantic similarity between resume and job description"""
    try:
        model = get_model()
        
        # Handle long texts by truncating
        max_length = 512
        resume_words = resume_text.split()
        jd_words = jd_text.split()
        
        if len(resume_words) > max_length:
            resume_text = ' '.join(resume_words[:max_length])
        if len(jd_words) > max_length:
            jd_text = ' '.join(jd_words[:max_length])
        
        resume_embedding = model.encode(resume_text)
        jd_embedding = model.encode(jd_text)
        
        similarity = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
        )[0][0]
        
        return float(similarity)
    
    except Exception as e:
        print(f"Similarity Calculation Error: {e}")
        return 0.0

# =====================================================
# EXPERIENCE SCORE
# =====================================================

def calculate_experience_score(resume_years, jd_years):
    if jd_years == 0:
        return 1.0
    
    if resume_years >= jd_years:
        return 1.0
    
    return resume_years / jd_years

# =====================================================
# SKILL SCORE
# =====================================================

def calculate_skill_score(resume_skills, jd_skills):
    """Calculate skill match with partial matching support"""
    matched = set()
    missing = set()
    partial_matches = {}
    
    # First pass: exact matches
    for jd_skill in jd_skills:
        if jd_skill in resume_skills:
            matched.add(jd_skill)
        else:
            # Second pass: partial matching
            found = False
            for resume_skill in resume_skills:
                if (jd_skill.lower() in resume_skill.lower() or 
                    resume_skill.lower() in jd_skill.lower()):
                    matched.add(jd_skill)
                    partial_matches[jd_skill] = resume_skill
                    found = True
                    break
            
            if not found:
                missing.add(jd_skill)
    
    score = len(matched) / len(jd_skills) if jd_skills else 0
    return score, matched, missing, partial_matches

# =====================================================
# MAIN MATCH FUNCTION
# =====================================================

def calculate_detailed_match(resume_text, jd_text):
    """Calculate detailed match between resume and job description"""
    
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)
    
    # =================================================
    # SKILLS
    # =================================================
    resume_skills = extract_skills(resume_clean)
    jd_skills = extract_skills(jd_clean)
    
    skill_score, matched_skills, missing_skills, skill_partial_matches = calculate_skill_score(
        resume_skills, jd_skills
    )
    
    # =================================================
    # KEYWORDS (IMPROVED WITH PHRASES)
    # =================================================
    # Extract keywords including phrases
    resume_keywords = extract_keywords(resume_clean, top_n=40)
    jd_keywords = extract_keywords(jd_clean, top_n=40)
    
    # Remove skill overlap to avoid double-counting
    resume_keywords = resume_keywords - {s.lower() for s in resume_skills}
    jd_keywords = jd_keywords - {s.lower() for s in jd_skills}
    
    # Calculate keyword score with enhanced matching
    keyword_match = match_keywords_with_context(
        resume_keywords, 
        jd_keywords, 
        resume_clean, 
        jd_clean
    )
    
    keyword_score = keyword_match['match_percentage'] / 100
    matched_keywords = keyword_match['matched']
    missing_keywords = keyword_match['missing']
    
    # =================================================
    # EXPERIENCE
    # =================================================
    resume_years = extract_experience_years(resume_text)
    jd_years = extract_experience_years(jd_text)
    
    experience_score = calculate_experience_score(resume_years, jd_years)
    
    # =================================================
    # SIMILARITY
    # =================================================
    similarity_score = calculate_similarity(resume_clean, jd_clean)
    
    # =================================================
    # WEIGHTS
    # =================================================
    weights = {
        "skills": 0.40,
        "experience": 0.15,
        "keywords": 0.15,
        "similarity": 0.30
    }
    
    final_score = (
        skill_score * weights["skills"] +
        experience_score * weights["experience"] +
        keyword_score * weights["keywords"] +
        similarity_score * weights["similarity"]
    ) * 100
    
    final_score = round(min(final_score, 100), 2)
    
    # =================================================
    # RETURN RESULTS
    # =================================================
    return {
        "overall": final_score,
        "breakdown": {
            "skills": round(skill_score * 100, 2),
            "keywords": round(keyword_score * 100, 2),
            "experience": round(experience_score * 100, 2),
            "similarity": round(similarity_score * 100, 2)
        },
        "details": {
            "resume_years": resume_years,
            "jd_years": jd_years,
            "resume_skills": list(resume_skills),
            "jd_skills": list(jd_skills),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "skill_partial_matches": skill_partial_matches,
            "resume_keywords": list(resume_keywords),
            "jd_keywords": list(jd_keywords),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "partial_keyword_matches": keyword_match.get('partial_matches', {}),
            "semantic_keyword_matches": keyword_match.get('semantic_matches', {})
        }
    }

# =====================================================
# INTERPRETATION
# =====================================================

def get_match_interpretation(score):
    """Get interpretation based on match score"""
    if score >= 90:
        return {
            "level": "EXCELLENT",
            "message": "Outstanding alignment with the role. Your skills and experience strongly match what they're looking for.",
            "action": "Apply with high confidence. Highlight your strongest matches in your cover letter.",
            "color": "success"
        }
    elif score >= 80:
        return {
            "level": "VERY STRONG",
            "message": "Very strong fit with minor improvements possible. You're a competitive candidate.",
            "action": "Apply with confidence. Address the missing keywords in your resume.",
            "color": "success"
        }
    elif score >= 70:
        return {
            "level": "STRONG",
            "message": "Strong match with a few areas to strengthen. You meet most key requirements.",
            "action": "Tailor your resume to include missing keywords and apply.",
            "color": "info"
        }
    elif score >= 60:
        return {
            "level": "GOOD",
            "message": "Good foundation but needs refinement. You have relevant skills but may lack specific keywords.",
            "action": "Incorporate missing keywords and consider adding relevant projects.",
            "color": "info"
        }
    elif score >= 50:
        return {
            "level": "MODERATE",
            "message": "Several important requirements are missing from your resume.",
            "action": "Focus on adding missing skills and keywords before applying.",
            "color": "warning"
        }
    elif score >= 35:
        return {
            "level": "LIMITED",
            "message": "Limited alignment with the role. Significant gaps in required skills.",
            "action": "Consider upskilling or finding roles that better match your current experience.",
            "color": "error"
        }
    else:
        return {
            "level": "WEAK",
            "message": "Minimal alignment with the role. Your background may be better suited for other positions.",
            "action": "Look for roles that match your existing skills or invest in relevant training.",
            "color": "error"
        }

# =====================================================
# LOCAL TERMINAL TEST
# =====================================================

if __name__ == "__main__":
    test_resume = """
    Digital Marketing Manager with 5 years experience
    Skills: SEO, SEM, Google Ads, GA4, HubSpot, Salesforce
    Achievements: Increased organic traffic by 150%
    """
    
    test_jd = """
    Digital Marketing Manager Needed
    Requirements:
    - 4+ years experience
    - SEO, SEM, Google Ads, GA4
    - Customer acquisition strategy
    - Lead generation
    - End-to-end campaign execution
    """
    
    try:
        result = calculate_detailed_match(test_resume, test_jd)
        print("\n" + "="*60)
        print("MATCH RESULT")
        print("="*60)
        print(f"Overall Score: {result['overall']}%")
        print(f"\nBreakdown:")
        for category, score in result['breakdown'].items():
            print(f"  {category.title()}: {score}%")
        print(f"\nSkills: {len(result['details']['matched_skills'])}/{len(result['details']['jd_skills'])} matched")
        print(f"Keywords: {len(result['details']['matched_keywords'])}/{len(result['details']['jd_keywords'])} matched")
        print(f"\nMatched Keywords: {result['details']['matched_keywords'][:5]}")
        print(f"Missing Keywords: {result['details']['missing_keywords'][:5]}")
        
        if result['details'].get('semantic_keyword_matches'):
            print(f"\nSemantic Matches: {len(result['details']['semantic_keyword_matches'])}")
        
        interpretation = get_match_interpretation(result['overall'])
        print(f"\nInterpretation: {interpretation['level']}")
        print(f"Action: {interpretation['action']}")
        
    except Exception as error:
        print(f"Test failed: {error}")
        import traceback
        traceback.print_exc()