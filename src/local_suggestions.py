# src/local_suggestions.py - GENERIC VERSION
import random

# Universal templates that work for ANY job
UNIVERSAL_TEMPLATES = [
    "Implemented {keyword} strategies that improved efficiency and productivity.",
    "Utilized {keyword} methodologies to streamline processes and workflows.",
    "Developed comprehensive {keyword} frameworks to achieve business objectives.",
    "Applied {keyword} techniques to analyze information and generate insights.",
    "Managed {keyword} initiatives from planning through successful execution.",
    "Created detailed {keyword} documentation to ensure consistency and compliance.",
    "Collaborated with teams on {keyword} projects achieving key goals.",
    "Designed and deployed {keyword} solutions addressing business needs.",
    "Led {keyword} efforts resulting in measurable improvements.",
    "Optimized {keyword} processes through innovation and best practices.",
    "Established {keyword} protocols that enhanced quality and reliability.",
    "Coordinated {keyword} activities across multiple departments.",
    "Spearheaded {keyword} programs that drove growth and success.",
    "Enhanced {keyword} capabilities through technology and training.",
    "Monitored and evaluated {keyword} performance against metrics.",
]

def generate_resume_bullets(missing_keywords, job_title=None):
    """
    Generate professional resume bullets for ANY job role
    """
    if not missing_keywords:
        return "✅ Your resume already covers the key keywords well!"
    
    # Clean and prepare keywords
    clean_keywords = []
    for keyword in missing_keywords:
        if isinstance(keyword, str) and len(keyword) > 3:
            # Remove any weird characters or newlines
            clean = ' '.join(keyword.split()).strip()
            if clean and clean.lower() not in ['none', 'na', 'null']:
                clean_keywords.append(clean)
    
    if not clean_keywords:
        return "No valid keywords to suggest improvements for."
    
    # Generate 3-4 professional suggestions
    suggestions = []
    used_keywords = set()
    
    for keyword in clean_keywords[:4]:  # Use up to 4 keywords
        if keyword in used_keywords:
            continue
            
        # Choose a random template
        template = random.choice(UNIVERSAL_TEMPLATES)
        
        # Format the bullet point
        formatted_keyword = keyword.title() if len(keyword.split()) == 1 else keyword
        bullet = template.format(keyword=formatted_keyword)
        suggestions.append(f"• {bullet}")
        used_keywords.add(keyword)
    
    return "\n".join(suggestions) if suggestions else "No suggestions generated."

def get_skill_recommendations(missing_skills):
    """
    Get learning resources for ANY skill
    """
    if not missing_skills:
        return "✅ All required skills are covered!"
    
    resources = []
    
    for skill in list(missing_skills)[:3]:  # Top 3 skills
        skill_name = skill.title()
        
        resources.append(f"\n📚 **{skill_name}**:")
        resources.append(f"   • Search for '{skill}' courses on Coursera, edX, or Udemy")
        resources.append(f"   • Check YouTube for '{skill} tutorials for beginners'")
        resources.append(f"   • Practice by applying {skill} to real projects")
    
    return "\n".join(resources)