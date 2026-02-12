# resume_enhancer.py
def generate_resume_enhancements(resume_text, jd_text, missing_skills):
    """Generate specific resume improvement suggestions"""
    
    enhancements = []
    
    # 1. Skills to add
    if missing_skills:
        enhancements.append("🔧 **ADD THESE SKILLS TO YOUR RESUME:**")
        for skill in missing_skills:
            enhancements.append(f"   • Add '{skill}' to your Skills section")
        
        # Suggest where to add skills in experience
        enhancements.append("\n   **Where to add them:**")
        enhancements.append("   • Microsoft Visio: 'Created process flowcharts using Microsoft Visio'")
        enhancements.append("   • Microsoft Teams: 'Collaborated with teams using Microsoft Teams for project coordination'")
        enhancements.append("   • Process Documentation: 'Developed comprehensive process documentation for system workflows'")
    
    # 2. Quantify achievements
    enhancements.append("\n📈 **QUANTIFY YOUR ACHIEVEMENTS:**")
    enhancements.append("   • Add percentages: 'Improved efficiency by 20%'")
    enhancements.append("   • Add numbers: 'Managed projects with $500K budget'")
    enhancements.append("   • Add metrics: 'Reduced processing time by 30%'")
    
    # 3. Action verbs
    enhancements.append("\n⚡ **USE STRONGER ACTION VERBS:**")
    enhancements.append("   • Instead of 'Did data analysis' → 'Spearheaded data analysis initiatives'")
    enhancements.append("   • Instead of 'Worked on projects' → 'Led end-to-end project implementation'")
    enhancements.append("   • Instead of 'Made reports' → 'Developed comprehensive analytical reports'")
    
    return "\n".join(enhancements)

# In resume_enhancer.py or create ats_checker.py
def check_ats_compatibility(resume_text):
    """Check for real ATS compatibility issues"""
    issues = []
    recommendations = []
    
    resume_lower = resume_text.lower()
    
    # Real ATS issues to check:
    
    # 1. Check for headers
    required_sections = ['experience', 'education', 'skills']
    for section in required_sections:
        if section not in resume_lower:
            issues.append(f"⚠️  Missing '{section.title()}' section header")
    
    # 2. Check for tables (can cause parsing issues)
    if '┌' in resume_text or '└' in resume_text or '│' in resume_text:
        issues.append("⚠️  Avoid using box-drawing characters (use simple formatting)")
    
    # 3. Check length
    word_count = len(resume_text.split())
    if word_count > 800:
        issues.append(f"⚠️  Resume might be too long ({word_count} words)")
        recommendations.append("Try to keep under 800 words for ATS readability")
    elif word_count < 200:
        issues.append(f"⚠️  Resume might be too short ({word_count} words)")
        recommendations.append("Add more detail to your experience section")
    
    # 4. Check contact info
    if '@' not in resume_text and 'phone' not in resume_lower:
        issues.append("⚠️  Ensure contact information is included")
    
    # 5. Positive checks
    positives = []
    if '•' in resume_text or '-' in resume_text:
        positives.append("✅ Uses bullet points (good for readability)")
    
    if any(word in resume_lower for word in ['achieved', 'improved', 'increased', 'reduced']):
        positives.append("✅ Uses action-oriented language")
    
    # Return formatted results
    result = []
    
    if issues:
        result.append("ATS COMPATIBILITY CHECK:")
        result.append("-" * 40)
        for issue in issues:
            result.append(issue)
    
    if recommendations:
        result.append("\nRECOMMENDATIONS:")
        for rec in recommendations:
            result.append(f"   • {rec}")
    
    if positives:
        result.append("\nSTRENGTHS:")
        for positive in positives:
            result.append(f"   {positive}")
    
    if not issues and not recommendations:
        result.append("✅ Your resume appears to be ATS-friendly!")
    
    return "\n".join(result)