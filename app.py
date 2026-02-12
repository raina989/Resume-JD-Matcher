# ResumeAlign/app.py - 
import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import your modules
from src.matcher import calculate_detailed_match, get_match_interpretation
from src.skill_gap import extract_skills
from src.keyword_gap import extract_keywords
from src.local_suggestions import generate_resume_bullets, get_skill_recommendations
from src.resume_enhancer import generate_resume_enhancements, check_ats_compatibility
from src.file_parser import extract_text_from_file
from src.report_generator import save_match_report, generate_html_report

# Page config
st.set_page_config(page_title="ResumeAlign", page_icon="🎯", layout="wide")

# ============ SESSION STATE INITIALIZATION ============
if 'resume' not in st.session_state:
    st.session_state.resume = ""
if 'jd' not in st.session_state:
    st.session_state.jd = ""
if 'results' not in st.session_state:
    st.session_state.results = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'clear_counter' not in st.session_state:
    st.session_state.clear_counter = 0
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis_id' not in st.session_state:
    st.session_state.current_analysis_id = None
if 'logout_triggered' not in st.session_state:
    st.session_state.logout_triggered = False

# ============ DATABASE ============
DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "resumealign.db"

# Create reports directory
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Analysis history table
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        analysis_id TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        match_score REAL,
        job_title TEXT,
        company_name TEXT,
        report_path TEXT,
        html_report_path TEXT,
        resume_snippet TEXT,
        jd_snippet TEXT,
        matched_skills TEXT,
        missing_skills TEXT,
        matched_keywords TEXT,
        missing_keywords TEXT,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )''')
    conn.commit()
    conn.close()

init_db()

def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def save_analysis_to_db(user_email, analysis_id, match_score, job_title, company_name, 
                       report_path, html_report_path, resume_snippet, jd_snippet,
                       matched_skills, missing_skills, matched_keywords, missing_keywords):
    """Save analysis to database for history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT INTO analysis_history 
                    (user_email, analysis_id, timestamp, match_score, job_title, 
                     company_name, report_path, html_report_path, resume_snippet, 
                     jd_snippet, matched_skills, missing_skills, matched_keywords, missing_keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_email, analysis_id, datetime.now(), match_score, job_title,
                     company_name, str(report_path), str(html_report_path), 
                     resume_snippet[:200], jd_snippet[:200],
                     json.dumps(list(matched_skills)), json.dumps(list(missing_skills)),
                     json.dumps(list(matched_keywords)), json.dumps(list(missing_keywords))))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving to history: {e}")
        return False

def load_analysis_history(user_email):
    """Load analysis history for a user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''SELECT analysis_id, timestamp, match_score, job_title, company_name,
                            report_path, html_report_path, matched_skills, missing_skills,
                            matched_keywords, missing_keywords
                    FROM analysis_history 
                    WHERE user_email = ? 
                    ORDER BY timestamp DESC''', (user_email,))
        history = c.fetchall()
        conn.close()
        return history
    except Exception as e:
        st.error(f"Error loading history: {e}")
        return []

# ============ UI ============
st.title("🎯 ResumeAlign")
st.markdown("Align your skills to your next role — intelligently.")
st.markdown("---")

# MAIN AREA
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    
    # Text area with dynamic key based on clear_counter
    resume = st.text_area(
        "Paste your resume text",
        value=st.session_state.resume,
        height=250,
        placeholder="Paste your resume here...",
        key=f"resume_input_{st.session_state.clear_counter}"
    )
    st.session_state.resume = resume
    
    # File upload with dynamic key
    uploaded_resume = st.file_uploader("Upload Resume (TXT, PDF, DOCX)", 
                                       type=['txt', 'pdf', 'docx'], 
                                       key=f"resume_upload_{st.session_state.clear_counter}")
    if uploaded_resume is not None:
        try:
            st.session_state.resume = extract_text_from_file(uploaded_resume)
            st.success("✅ Resume uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

with col2:
    st.subheader("📋 Job Description")
    
    # Text area with dynamic key based on clear_counter
    jd = st.text_area(
        "Paste job description text",
        value=st.session_state.jd,
        height=250,
        placeholder="Paste job description here...",
        key=f"jd_input_{st.session_state.clear_counter}"
    )
    st.session_state.jd = jd
    
    # File upload with dynamic key
    uploaded_jd = st.file_uploader("Upload Job Description (TXT, PDF, DOCX)", 
                                   type=['txt', 'pdf', 'docx'], 
                                   key=f"jd_upload_{st.session_state.clear_counter}")
    if uploaded_jd is not None:
        try:
            st.session_state.jd = extract_text_from_file(uploaded_jd)
            st.success("✅ Job description uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# BUTTONS
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 ANALYZE MATCH", type="primary", use_container_width=True, key="analyze_button"):
        if st.session_state.resume and st.session_state.jd:
            with st.spinner("🔬 Analyzing your resume against job description..."):
                
                # ---- EXTRACT SKILLS ----
                resume_skills = extract_skills(st.session_state.resume)
                jd_skills = extract_skills(st.session_state.jd)
                
                matched_skills = resume_skills & jd_skills
                missing_skills = jd_skills - resume_skills
                
                # ---- EXTRACT KEYWORDS ----
                resume_keywords = extract_keywords(st.session_state.resume, top_n=20)
                jd_keywords = extract_keywords(st.session_state.jd, top_n=20)
                
                matched_keywords = resume_keywords & jd_keywords
                missing_keywords = jd_keywords - resume_keywords
                
                # ---- CALCULATE MATCH SCORE ----
                match_result = calculate_detailed_match(
                    st.session_state.resume, 
                    st.session_state.jd
                )
                
                # ---- GENERATE SUGGESTIONS ----
                bullet_suggestions = generate_resume_bullets(
                    list(missing_keywords)[:5], 
                    job_title="this position"
                )
                
                skill_recommendations = get_skill_recommendations(list(missing_skills))
                
                enhancements = generate_resume_enhancements(
                    st.session_state.resume,
                    st.session_state.jd,
                    list(missing_skills)[:5]
                )
                
                ats_check = check_ats_compatibility(st.session_state.resume)
                
                # ---- GENERATE REPORTS ----
                # Create unique ID for this analysis
                analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Extract job title from JD (simple version)
                job_title = "Software Developer"  # Default
                if "software" in st.session_state.jd.lower():
                    job_title = "Software Developer"
                elif "data" in st.session_state.jd.lower():
                    job_title = "Data Analyst"
                elif "project" in st.session_state.jd.lower():
                    job_title = "Project Manager"
                elif "product" in st.session_state.jd.lower():
                    job_title = "Product Manager"
                elif "marketing" in st.session_state.jd.lower():
                    job_title = "Marketing Specialist"
                
                # Save text report
                report_file = save_match_report(
                    match_result=match_result,
                    missing_skills=missing_skills,
                    missing_keywords=missing_keywords,
                    resume_filename="resume.txt",
                    jd_filename="job_description.txt",
                    output_dir="reports"
                )
                
                # Save HTML report
                html_report = generate_html_report(
                    match_result=match_result,
                    missing_skills=missing_skills,
                    missing_keywords=missing_keywords,
                    resume_filename="resume.txt",
                    jd_filename="job_description.txt",
                    output_dir="reports"
                )
                
                # Save to database if user is logged in and not guest
                if st.session_state.user and st.session_state.user != "guest":
                    save_analysis_to_db(
                        user_email=st.session_state.user,
                        analysis_id=analysis_id,
                        match_score=match_result['overall'],
                        job_title=job_title,
                        company_name="",  # Could extract from JD
                        report_path=report_file,
                        html_report_path=html_report,
                        resume_snippet=st.session_state.resume[:200],
                        jd_snippet=st.session_state.jd[:200],
                        matched_skills=matched_skills,
                        missing_skills=missing_skills,
                        matched_keywords=matched_keywords,
                        missing_keywords=missing_keywords
                    )
                
                # Add to session state history
                history_entry = {
                    'id': analysis_id,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'score': match_result['overall'],
                    'job_title': job_title,
                    'report_path': str(report_file),
                    'html_report_path': str(html_report),
                    'matched_skills_count': len(matched_skills),
                    'missing_skills_count': len(missing_skills),
                    'matched_skills': list(matched_skills),
                    'missing_skills': list(missing_skills),
                    'matched_keywords': list(matched_keywords),
                    'missing_keywords': list(missing_keywords)
                }
                
                # Add to beginning of history list
                st.session_state.analysis_history.insert(0, history_entry)
                st.session_state.current_analysis_id = analysis_id
                
                # ---- STORE ALL RESULTS ----
                st.session_state.results = {
                    'score': match_result['overall'],
                    'breakdown': match_result['breakdown'],
                    'matched_skills': list(matched_skills),
                    'missing_skills': list(missing_skills),
                    'matched_keywords': list(matched_keywords),
                    'missing_keywords': list(missing_keywords),
                    'bullet_suggestions': bullet_suggestions,
                    'skill_recommendations': skill_recommendations,
                    'enhancements': enhancements,
                    'ats_check': ats_check,
                    'interpretation': get_match_interpretation(match_result['overall']),
                    'report_path': str(report_file),
                    'html_report_path': str(html_report),
                    'analysis_id': analysis_id,
                    'job_title': job_title
                }
                st.session_state.analysis_done = True
                
                st.success("✅ Analysis complete! Reports generated.")
        else:
            st.error("⚠️ Please provide both resume and job description")

with col2:
    if st.button("📋 SAMPLE DATA", use_container_width=True, key="sample_button"):
        st.session_state.resume = """John Doe - Software Developer
123 Main St, San Francisco, CA | john.doe@email.com

SUMMARY
Experienced software developer with 3+ years in full-stack development.

TECHNICAL SKILLS
• Python, JavaScript, React, SQL, Git

WORK EXPERIENCE
Senior Developer | Tech Solutions Inc. | Jan 2021 - Present
• Developed web applications using Python and React
• Implemented RESTful APIs
• Improved performance by 40%

PROJECTS
• E-commerce Platform: Built with React and Node.js
• Data Dashboard: Created interactive visualizations with Python

EDUCATION
B.S. Computer Science, University of Technology, 2020"""
        
        st.session_state.jd = """Software Developer Job Description

We are seeking a skilled Software Developer to join our growing team.

REQUIREMENTS:
• 2+ years of software development experience
• Strong proficiency in Python and JavaScript
• Experience with React.js for frontend development
• Knowledge of SQL and database design
• Experience building RESTful APIs
• Git version control
• AWS or Docker experience preferred
• Excellent problem-solving skills
• Strong communication and teamwork abilities

NICE TO HAVE:
• Experience with Django or Flask
• Knowledge of CI/CD pipelines
• Bachelor's degree in Computer Science or related field"""
        
        st.session_state.results = None
        st.session_state.analysis_done = False

with col3:
    # CLEAR BUTTON - Clears EVERYTHING in ONE CLICK - NO LOOPS
    if st.button("🗑️ CLEAR", use_container_width=True, key="clear_button_main"):
        # 1. Clear text content
        st.session_state.resume = ""
        st.session_state.jd = ""
        
        # 2. Clear analysis results
        st.session_state.results = None
        st.session_state.analysis_done = False
        
        # 3. Increment clear counter to force ALL widgets to refresh with new keys
        st.session_state.clear_counter += 1
        
        # 4. Show success message
        st.success("✅ All content cleared!")

# ============ DISPLAY RESULTS ============
if st.session_state.results and st.session_state.analysis_done:
    r = st.session_state.results
    
    st.markdown("---")
    st.header("📊 ANALYSIS RESULTS")
    
    # ----- OVERALL SCORE -----
    score = r['score']
    
    # Score with colored background
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if score >= 70:
            st.success(f"### 🎯 EXCELLENT MATCH: {score}%")
        elif score >= 50:
            st.warning(f"### 📈 GOOD MATCH: {score}%")
        else:
            st.error(f"### 💪 NEEDS IMPROVEMENT: {score}%")
        
        st.progress(score/100)
        
        # Interpretation
        st.info(r['interpretation']['message'])
    
    # ----- DOWNLOAD BUTTONS -----
    col1, col2 = st.columns(2)
    with col1:
        if 'report_path' in r and Path(r['report_path']).exists():
            with open(r['report_path'], 'r', encoding='utf-8') as f:
                report_content = f.read()
            st.download_button(
                label="📄 Download Text Report",
                data=report_content,
                file_name=f"match_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with col2:
        if 'html_report_path' in r and Path(r['html_report_path']).exists():
            with open(r['html_report_path'], 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.download_button(
                label="📊 Download HTML Report",
                data=html_content,
                file_name=f"match_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
    
    # ----- METRICS -----
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Match Score", f"{score}%")
    with col2:
        if r['missing_skills']:
            total_skills = len(r['matched_skills']) + len(r['missing_skills'])
            st.metric("Skills Matched", 
                      f"{len(r['matched_skills'])}/{total_skills}")
        else:
            st.metric("Skills Matched", f"{len(r['matched_skills'])}")
    with col3:
        if r['missing_keywords']:
            total_keywords = len(r['matched_keywords']) + len(r['missing_keywords'])
            st.metric("Keywords Found", 
                      f"{len(r['matched_keywords'])}/{total_keywords}")
        else:
            st.metric("Keywords Found", f"{len(r['matched_keywords'])}")
    with col4:
        if 'breakdown' in r and 'experience' in r['breakdown']:
            st.metric("Experience Match", f"{r['breakdown']['experience']:.0f}%")
    
    # ----- VISUAL PROGRESS BARS -----
    st.markdown("---")
    st.subheader("📈 MATCH BREAKDOWN")
    
    if 'breakdown' in r:
        for category, score_value in r['breakdown'].items():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{category.title()}**")
            with col2:
                bar_length = int(score_value / 5)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                st.write(f"{bar} {score_value:.1f}%")
    
    # ----- SKILLS COMPARISON -----
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Skills")
        if r['matched_skills']:
            for skill in sorted(r['matched_skills'])[:15]:
                st.write(f"• {skill.title()}")
            if len(r['matched_skills']) > 15:
                st.caption(f"... and {len(r['matched_skills']) - 15} more")
        else:
            st.info("No skills matched yet")
    
    with col2:
        st.subheader("❌ Missing Skills")
        if r['missing_skills']:
            for skill in sorted(r['missing_skills'])[:15]:
                st.write(f"• {skill.title()}")
            if len(r['missing_skills']) > 15:
                st.caption(f"... and {len(r['missing_skills']) - 15} more")
        else:
            st.success("All required skills covered!")
    
    # ----- KEYWORDS -----
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Keywords")
        if r['matched_keywords']:
            keywords_display = sorted(r['matched_keywords'])[:20]
            st.write(", ".join(keywords_display))
            if len(r['matched_keywords']) > 20:
                st.caption(f"... and {len(r['matched_keywords']) - 20} more")
        else:
            st.info("No keywords matched")
    
    with col2:
        st.subheader("🔑 Missing Keywords")
        if r['missing_keywords']:
            keywords_display = sorted(r['missing_keywords'])[:20]
            st.write(", ".join(keywords_display))
            if len(r['missing_keywords']) > 20:
                st.caption(f"... and {len(r['missing_keywords']) - 20} more")
        else:
            st.success("All keywords covered!")
    
    # ----- AI SUGGESTIONS -----
    st.markdown("---")
    st.header("🚀 AI-POWERED SUGGESTIONS")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Resume Bullets", 
        "📚 Learning Resources", 
        "⚡ Enhancements",
        "🤖 ATS Check"
    ])
    
    with tab1:
        st.subheader("Add these bullet points to your resume:")
        if 'bullet_suggestions' in r and r['bullet_suggestions']:
            st.markdown(r['bullet_suggestions'])
        else:
            st.info("No bullet suggestions available")
    
    with tab2:
        st.subheader("Learning Resources for Missing Skills:")
        if 'skill_recommendations' in r and r['skill_recommendations']:
            st.markdown(r['skill_recommendations'])
        else:
            st.info("No skill recommendations available")
    
    with tab3:
        st.subheader("Resume Enhancement Tips:")
        if 'enhancements' in r and r['enhancements']:
            st.markdown(r['enhancements'])
        else:
            st.info("No enhancement tips available")
    
    with tab4:
        st.subheader("ATS Compatibility Check:")
        if 'ats_check' in r and r['ats_check']:
            st.markdown(r['ats_check'])
        else:
            st.info("No ATS check available")
    
    # ----- ACTION PLAN -----
    st.markdown("---")
    st.subheader("📋 3-STEP ACTION PLAN")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**1️⃣ IMMEDIATE (5 min)**")
        if r['missing_skills']:
            st.write(f"Add {min(3, len(r['missing_skills']))} missing skills to your resume")
        else:
            st.write("Review your resume for keyword optimization")
    
    with col2:
        st.info("**2️⃣ TODAY (20 min)**")
        if r['missing_keywords']:
            st.write(f"Incorporate {min(3, len(r['missing_keywords']))} keywords into experience bullets")
        else:
            st.write("Quantify 2-3 achievements with metrics")
    
    with col3:
        st.info("**3️⃣ THIS WEEK (1 hour)**")
        st.write("Build a project or take a course in a missing skill area")

# ============ SIDEBAR ============
with st.sidebar:
    st.header("👤 ACCOUNT")
    st.markdown("---")
    
    if not st.session_state.user:
        tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("LOGIN", type="primary", use_container_width=True):
                    if email and password:
                        st.session_state.user = email
                        # Load user's history
                        history = load_analysis_history(email)
                        st.session_state.analysis_history = []
                        for h in history:
                            st.session_state.analysis_history.append({
                                'id': h[0],
                                'timestamp': h[1],
                                'score': h[2],
                                'job_title': h[3] or 'Unknown Position',
                                'company_name': h[4] or '',
                                'report_path': h[5],
                                'html_report_path': h[6],
                                'matched_skills': json.loads(h[7]) if h[7] else [],
                                'missing_skills': json.loads(h[8]) if h[8] else [],
                                'matched_keywords': json.loads(h[9]) if h[9] else [],
                                'missing_keywords': json.loads(h[10]) if h[10] else [],
                                'matched_skills_count': len(json.loads(h[7])) if h[7] else 0,
                                'missing_skills_count': len(json.loads(h[8])) if h[8] else 0
                            })
                        st.rerun()
        
        with tab2:
            with st.form("signup_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                name = st.text_input("Full Name", placeholder="John Doe")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("CREATE ACCOUNT", type="primary", use_container_width=True):
                    if email and name and password and len(password) >= 6:
                        st.session_state.user = email
                        st.session_state.analysis_history = []
                        st.rerun()
        
        st.markdown("---")
        
        if st.button("👤 CONTINUE AS GUEST", use_container_width=True):
            st.session_state.user = "guest"
            st.session_state.analysis_history = []
            st.rerun()
    
    else:
        st.success(f"✅ Logged in as {st.session_state.user.split('@')[0] if '@' in st.session_state.user else 'Guest'}")
        
        # ----- ANALYSIS HISTORY SECTION -----
        if st.session_state.user != "guest" and st.session_state.analysis_history:
            st.markdown("---")
            st.header("📜 ANALYSIS HISTORY")
            
            # Display last 5 analyses
            for i, analysis in enumerate(st.session_state.analysis_history[:5]):
                # Color code based on score
                score = analysis['score']
                if score >= 70:
                    score_color = "🟢"
                elif score >= 50:
                    score_color = "🟡"
                else:
                    score_color = "🔴"
                
                # Create expander for each analysis
                with st.expander(f"{score_color} {analysis['job_title']} - {score}% ({analysis['timestamp']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Match Score", f"{score}%")
                        st.write(f"**Matched Skills:** {analysis.get('matched_skills_count', 0)}")
                        st.write(f"**Missing Skills:** {analysis.get('missing_skills_count', 0)}")
                    
                    with col2:
                        # Download buttons for reports
                        if 'report_path' in analysis and Path(analysis['report_path']).exists():
                            with open(analysis['report_path'], 'r', encoding='utf-8') as f:
                                report_content = f.read()
                            st.download_button(
                                label="📄 Download Report",
                                data=report_content,
                                file_name=f"report_{analysis['id']}.txt",
                                mime="text/plain",
                                key=f"download_{analysis['id']}",
                                use_container_width=True
                            )
                        
                        if 'html_report_path' in analysis and Path(analysis['html_report_path']).exists():
                            with open(analysis['html_report_path'], 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            st.download_button(
                                label="📊 Download HTML",
                                data=html_content,
                                file_name=f"report_{analysis['id']}.html",
                                mime="text/html",
                                key=f"download_html_{analysis['id']}",
                                use_container_width=True
                            )
        
        elif st.session_state.user != "guest":
            st.info("📭 No analysis history yet. Run your first analysis!")
        
        st.markdown("---")
        
        # LOGOUT BUTTON 
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary", key="logout_button"):
            # Clear ALL user-related session state
            st.session_state.user = None
            st.session_state.analysis_history = []
            st.session_state.results = None
            st.session_state.analysis_done = False
            st.session_state.resume = ""
            st.session_state.jd = ""
            st.session_state.clear_counter += 1
            st.session_state.current_analysis_id = None
            
            # rerun 
            st.rerun()
    
    st.markdown("---")
    st.header("📌 HOW TO USE")
    st.markdown("""
    1. **Paste** or **upload** your resume
    2. **Paste** or **upload** job description
    3. Click **ANALYZE MATCH**
    4. Review your AI-powered suggestions
    5. **Download** detailed reports
    6. **History** saves automatically for logged-in users
    """)
    
    st.markdown("---")
    st.caption("© 2026 ResumeAlign")