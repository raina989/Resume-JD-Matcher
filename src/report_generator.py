# report_generator.py
import os
from datetime import datetime

def save_match_report(match_result, missing_skills, missing_keywords,
                     resume_filename, jd_filename, output_dir="../reports"):
    """
    Save detailed match report to a file
    
    Parameters:
    - match_result: Dictionary with 'overall' and 'breakdown' scores
    - missing_skills: Set of missing skills
    - missing_keywords: Set of missing keywords  
    - resume_filename: Name of resume file
    - jd_filename: Name of job description file
    - output_dir: Directory to save reports (default: ../reports)
    """
    
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"match_report_{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RESUME - JOB DESCRIPTION MATCH ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        # Report metadata
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Resume: {resume_filename}\n")
        f.write(f"Job Description: {jd_filename}\n")
        f.write("-" * 70 + "\n\n")
        
        # Overall Score
        f.write("📊 OVERALL ASSESSMENT\n")
        f.write("-" * 40 + "\n")
        f.write(f"Match Score: {match_result['overall']}%\n\n")
        
        # Score Interpretation
        score = match_result['overall']
        if score >= 80:
            rating = "EXCELLENT"
            interpretation = "Your resume is very well aligned with this position. Consider applying!"
        elif score >= 60:
            rating = "GOOD" 
            interpretation = "Your resume has a solid foundation. Minor improvements recommended."
        elif score >= 40:
            rating = "MODERATE"
            interpretation = "Significant improvements needed for this role."
        else:
            rating = "LOW"
            interpretation = "This may not be the best fit with your current resume."
        
        f.write(f"Rating: {rating}\n")
        f.write(f"Interpretation: {interpretation}\n\n")
        
        # Score Breakdown
        f.write("📈 SCORE BREAKDOWN\n")
        f.write("-" * 40 + "\n")
        for category, score in match_result['breakdown'].items():
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            f.write(f"{category.capitalize():15} {score:6.1f}% |{bar}|\n")
        f.write("\n")
        
        # Skills Analysis
        f.write("🔧 SKILLS ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        # Get skills counts
        if 'skills' in match_result['breakdown']:
            skill_score = match_result['breakdown']['skills']
            f.write(f"Skills Match: {skill_score:.1f}%\n")
        
        if missing_skills:
            f.write(f"\nMissing Skills ({len(missing_skills)}):\n")
            for i, skill in enumerate(sorted(missing_skills), 1):
                f.write(f"  {i}. {skill}\n")
        else:
            f.write("\n✅ All required skills are covered!\n")
        
        # Keywords Analysis  
        f.write("\n🔑 KEYWORDS ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        if 'keywords' in match_result['breakdown']:
            keyword_score = match_result['breakdown']['keywords']
            f.write(f"Keywords Match: {keyword_score:.1f}%\n")
        
        if missing_keywords:
            f.write(f"\nMissing Keywords ({len(missing_keywords)}):\n")
            # Group keywords for better readability
            keywords_list = sorted(missing_keywords)
            for i in range(0, len(keywords_list), 5):
                chunk = keywords_list[i:i+5]
                f.write("  • " + ", ".join(chunk) + "\n")
        else:
            f.write("\n✅ Excellent keyword coverage!\n")
        
        # Improvement Recommendations
        f.write("\n" + "=" * 70 + "\n")
        f.write("🚀 ACTIONABLE IMPROVEMENTS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("IMMEDIATE ACTIONS (Do today):\n")
        f.write("-" * 30 + "\n")
        
        if missing_skills:
            f.write("1. ADD THESE SKILLS TO YOUR RESUME:\n")
            for skill in sorted(missing_skills)[:3]:  # Top 3
                f.write(f"   • Add '{skill}' to your Skills section\n")
        
        if missing_keywords:
            f.write("\n2. INCORPORATE THESE KEYWORDS:\n")
            for keyword in sorted(missing_keywords)[:5]:  # Top 5
                f.write(f"   • Use '{keyword}' in your experience bullets\n")
        
        f.write("\n3. QUANTIFY ACHIEVEMENTS:\n")
        f.write("   • Add numbers and percentages to your accomplishments\n")
        f.write("   • Example: 'Improved efficiency by 25%' instead of 'Improved efficiency'\n")
        
        f.write("\n\nWEEKLY GOALS (Complete this week):\n")
        f.write("-" * 30 + "\n")
        f.write("1. Update your LinkedIn profile with the same keywords\n")
        f.write("2. Practice explaining how your skills match the job requirements\n")
        f.write("3. Network with 2-3 people in similar roles\n")
        
        # ATS Tips
        f.write("\n" + "=" * 70 + "\n")
        f.write("🤖 ATS (APPLICANT TRACKING SYSTEM) TIPS\n")
        f.write("=" * 70 + "\n\n")
        f.write("✅ DO:\n")
        f.write("   • Use standard section headers (Experience, Education, Skills)\n")
        f.write("   • Include keywords from the job description\n")
        f.write("   • Use a clean, simple format\n")
        f.write("   • Save as PDF for consistency\n\n")
        
        f.write("❌ AVOID:\n")
        f.write("   • Graphics, images, or logos\n")
        f.write("   • Tables or text boxes\n")
        f.write("   • Uncommon fonts\n")
        f.write("   • Headers/footers that might get cut off\n")
        
        # Quick Tips based on score
        f.write("\n" + "=" * 70 + "\n")
        f.write("💡 QUICK TIPS\n")
        f.write("=" * 70 + "\n\n")
        
        tips = generate_quick_tips(match_result['overall'])
        for tip in tips:
            f.write(f"• {tip}\n")
        
        # Footer
        f.write("\n" + "=" * 70 + "\n")
        f.write("Generated by Resume-JD Matcher\n")
        f.write("=" * 70 + "\n")
    
    return output_file

def generate_quick_tips(match_score):
    """Generate quick tips based on match score"""
    tips = []
    
    if match_score >= 80:
        tips.append("✅ Your resume is ready! Apply now.")
        tips.append("✅ Highlight your matched skills in your cover letter")
        tips.append("✅ Prepare stories about your key achievements")
        tips.append("✅ Customize your LinkedIn profile to match this role")
        tips.append("✅ Research the company before applying")
    elif match_score >= 60:
        tips.append("📝 Spend 30 minutes adding missing keywords to your resume")
        tips.append("📝 Update your skills section with missing skills")
        tips.append("📝 Tailor your summary/objective to this specific role")
        tips.append("📝 Quantify 2-3 achievements with numbers")
        tips.append("📝 Apply within 24 hours after making improvements")
    else:
        tips.append("🔄 Consider if this is the right role for you")
        tips.append("🔄 Focus on developing missing skills through courses/projects")
        tips.append("🔄 Look for roles that better match your current skills")
        tips.append("🔄 Build a portfolio project showcasing relevant skills")
        tips.append("🔄 Network with people in similar roles for advice")
    
    return tips

def generate_html_report(match_result, missing_skills, missing_keywords, 
                        resume_filename, jd_filename, output_dir="../reports"):
    """Save report as HTML for better viewing (OPTIONAL)"""
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"match_report_{timestamp}.html")
    
    # Determine color based on score
    score_color = "#27ae60" if match_result['overall'] >= 70 else "#e74c3c" if match_result['overall'] < 40 else "#f39c12"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume-JD Match Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
            .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #3498db; background: #f8f9fa; border-radius: 5px; }}
            .skill {{ display: inline-block; background: {'#2ecc71' if not missing_skills else '#e74c3c'}; 
                     color: white; padding: 5px 10px; margin: 5px; border-radius: 3px; }}
            .tip {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; border-radius: 3px; }}
            .badge {{ background: #3498db; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Resume-JD Match Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Resume: {resume_filename} | JD: {jd_filename}</p>
        </div>
        
        <div class="section">
            <h2>Overall Match Score</h2>
            <div class="score">{match_result['overall']}%</div>
            <p>
                <span class="badge">{'EXCELLENT' if match_result['overall'] >= 80 else 'GOOD' if match_result['overall'] >= 60 else 'MODERATE' if match_result['overall'] >= 40 else 'NEEDS WORK'}</span>
            </p>
        </div>
        
        <div class="section">
            <h2>Score Breakdown</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Score</th>
                    <th>Progress</th>
                </tr>
    """
    
    for category, score in match_result['breakdown'].items():
        bar_width = int(score)
        html_content += f"""
                <tr>
                    <td>{category.capitalize()}</td>
                    <td>{score}%</td>
                    <td>
                        <div style="width: 200px; background: #ecf0f1; border-radius: 3px;">
                            <div style="width: {bar_width}%; background: #3498db; height: 20px; border-radius: 3px;"></div>
                        </div>
                    </td>
                </tr>
        """
    
    html_content += f"""
            </table>
        </div>
        
        <div class="section">
            <h2>Missing Skills</h2>
    """
    
    if missing_skills:
        html_content += "<p>Add these skills to your resume:</p><div>"
        for skill in sorted(missing_skills):
            html_content += f'<span class="skill">{skill}</span>'
        html_content += "</div>"
    else:
        html_content += "<p>✅ All required skills are covered!</p>"
    
    html_content += f"""
        </div>
        
        <div class="section">
            <h2>Quick Tips</h2>
    """
    
    tips = generate_quick_tips(match_result['overall'])
    for tip in tips:
        html_content += f'<div class="tip">{tip}</div>'
    
    html_content += """
        </div>
        
        <div class="section">
            <h2>Next Steps</h2>
            <ol>
                <li>Update your resume with missing skills</li>
                <li>Incorporate keywords into experience bullets</li>
                <li>Quantify achievements with numbers</li>
                <li>Apply within 48 hours while analysis is fresh</li>
                <li>Follow up with the hiring manager on LinkedIn</li>
            </ol>
        </div>
        
        <div class="section" style="background: #e8f4f8; border-left-color: #1abc9c;">
            <h2>📞 Need Help?</h2>
            <p>For personalized resume review or career coaching, contact professionals in your network or consider career services from your alma mater.</p>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file