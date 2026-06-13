# app.py
import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os
import json

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

# Page config (ONLY RUNS ONCE AT THE VERY TOP)
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

# ============ DATABASE SETUPS ============
DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "resumealign.db"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        email TEXT UNIQUE NOT NULL, 
        name TEXT NOT NULL, 
        password TEXT NOT NULL, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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
        semantic_matches TEXT,
        FOREIGN KEY (user_email) REFERENCES users(email))''')
    conn.commit()
    conn.close()

init_db()

def hash_pwd(p): 
    return hashlib.sha256(p.encode()).hexdigest()

def save_analysis_to_db(user_email, analysis_id, match_score, job_title, company_name, 
                        report_path, html_report_path, resume_snippet, jd_snippet, 
                        matched_skills, missing_skills, matched_keywords, missing_keywords,
                        semantic_matches):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT INTO analysis_history 
            (user_email, analysis_id, timestamp, match_score, job_title, company_name, 
             report_path, html_report_path, resume_snippet, jd_snippet, 
             matched_skills, missing_skills, matched_keywords, missing_keywords, semantic_matches) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (user_email, analysis_id, datetime.now(), match_score, job_title, company_name, 
             str(report_path), str(html_report_path), resume_snippet[:200], jd_snippet[:200], 
             json.dumps(list(matched_skills)), json.dumps(list(missing_skills)), 
             json.dumps(list(matched_keywords)), json.dumps(list(missing_keywords)),
             json.dumps(semantic_matches)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database save error: {e}")
        return False

def load_analysis_history(user_email):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''SELECT analysis_id, timestamp, match_score, job_title, company_name, 
            report_path, html_report_path, matched_skills, missing_skills, 
            matched_keywords, missing_keywords, semantic_matches 
            FROM analysis_history WHERE user_email = ? ORDER BY timestamp DESC''', (user_email,))
        history = c.fetchall()
        conn.close()
        return history
    except Exception as e:
        print(f"Load history error: {e}")
        return []

# ============ UI LAYOUT ============
st.title("🎯 ResumeAlign")
st.markdown("Align your skills to your next role — intelligently.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    resume = st.text_area("Paste your resume text", value=st.session_state.resume, 
                          height=250, placeholder="Paste your resume here...", 
                          key=f"resume_input_{st.session_state.clear_counter}")
    st.session_state.resume = resume
    
    uploaded_resume = st.file_uploader("Upload Resume (TXT, PDF, DOCX)", 
                                        type=['txt', 'pdf', 'docx'], 
                                        key=f"resume_upload_{st.session_state.clear_counter}")
    if uploaded_resume is not None:
        try: 
            st.session_state.resume = extract_text_from_file(uploaded_resume)
        except Exception as e: 
            st.error(f"Error reading file: {e}")

with col2:
    st.subheader("📋 Job Description")
    jd = st.text_area("Paste job description text", value=st.session_state.jd, 
                      height=250, placeholder="Paste job description here...", 
                      key=f"jd_input_{st.session_state.clear_counter}")
    st.session_state.jd = jd
    
    uploaded_jd = st.file_uploader("Upload Job Description (TXT, PDF, DOCX)", 
                                    type=['txt', 'pdf', 'docx'], 
                                    key=f"jd_upload_{st.session_state.clear_counter}")
    if uploaded_jd is not None:
        try: 
            st.session_state.jd = extract_text_from_file(uploaded_jd)
        except Exception as e: 
            st.error(f"Error reading file: {e}")

# ============ CONTROLS AND BUTTONS ============
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button("🔍 ANALYZE MATCH", type="primary", use_container_width=True, key="analyze_button"):
        if st.session_state.resume and st.session_state.jd:
            with st.spinner("🔬 Analyzing your resume against job description..."):
                match_result = calculate_detailed_match(st.session_state.resume, st.session_state.jd)
                
                matched_skills = set(match_result["details"]["matched_skills"])
                missing_skills = set(match_result["details"]["missing_skills"])
                matched_keywords = set(match_result["details"]["matched_keywords"])
                missing_keywords = set(match_result["details"]["missing_keywords"])
                
                # Get semantic matches from the enhanced matcher
                semantic_matches = match_result["details"].get("semantic_keyword_matches", {})
                partial_matches = match_result["details"].get("partial_keyword_matches", {})
                skill_partial_matches = match_result["details"].get("skill_partial_matches", {})
                
                # Determine job title from JD
                job_title = "Software Developer"
                if "marketing" in st.session_state.jd.lower(): 
                    job_title = "Marketing Specialist"
                elif "data" in st.session_state.jd.lower(): 
                    job_title = "Data Analyst"
                elif "project" in st.session_state.jd.lower(): 
                    job_title = "Project Manager"
                elif "sales" in st.session_state.jd.lower():
                    job_title = "Sales Representative"
                elif "product" in st.session_state.jd.lower():
                    job_title = "Product Manager"
                
                bullet_suggestions = generate_resume_bullets(list(missing_keywords)[:5], job_title=job_title)
                skill_recommendations = get_skill_recommendations(list(missing_skills))
                enhancements = generate_resume_enhancements(st.session_state.resume, st.session_state.jd, list(missing_skills)[:5])
                ats_check = check_ats_compatibility(st.session_state.resume)
                
                analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                report_file = save_match_report(match_result, missing_skills, missing_keywords, 
                                                "resume.txt", "job_description.txt", "reports")
                html_report = generate_html_report(match_result, missing_skills, missing_keywords, 
                                                   "resume.txt", "job_description.txt", "reports")
                
                if st.session_state.user and st.session_state.user != "guest":
                    save_analysis_to_db(st.session_state.user, analysis_id, match_result['overall'], 
                                       job_title, "", report_file, html_report, 
                                       st.session_state.resume, st.session_state.jd, 
                                       matched_skills, missing_skills, matched_keywords, missing_keywords,
                                       semantic_matches)
                
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
                    'missing_keywords': list(missing_keywords),
                    'semantic_matches': semantic_matches,
                    'partial_matches': partial_matches
                }
                st.session_state.analysis_history.insert(0, history_entry)
                st.session_state.current_analysis_id = analysis_id
                
                st.session_state.results = {
                    'score': match_result['overall'], 
                    'breakdown': match_result['breakdown'], 
                    'matched_skills': list(matched_skills), 
                    'missing_skills': list(missing_skills), 
                    'matched_keywords': list(matched_keywords), 
                    'missing_keywords': list(missing_keywords),
                    'semantic_matches': semantic_matches,
                    'partial_matches': partial_matches,
                    'skill_partial_matches': skill_partial_matches,
                    'bullet_suggestions': bullet_suggestions, 
                    'skill_recommendations': skill_recommendations, 
                    'enhancements': enhancements, 
                    'ats_check': ats_check, 
                    'interpretation': get_match_interpretation(match_result['overall']), 
                    'report_path': str(report_file), 
                    'html_report_path': str(html_report), 
                    'analysis_id': analysis_id, 
                    'job_title': job_title,
                    'jd_skills': match_result['details'].get('jd_skills', []),
                    'resume_years': match_result['details'].get('resume_years', 0),
                    'jd_years': match_result['details'].get('jd_years', 0)
                }
                st.session_state.analysis_done = True
                st.success("✅ Analysis complete!")
                st.rerun()
        else:
            st.error("⚠️ Please provide both fields")

with col_b2:
    if st.button("📋 SAMPLE DATA", use_container_width=True, key="sample_button"):
        st.session_state.resume = """John Doe - Digital Marketing Manager
Experience: 5 years in digital marketing
Skills: SEO, SEM, Google Ads, Facebook Ads, GA4, HubSpot, Salesforce
Achievements: Increased organic traffic by 150%, reduced CAC by 30%"""
        
        st.session_state.jd = """Digital Marketing Manager Needed
Requirements:
- 4+ years experience in digital marketing
- Strong SEO and SEM skills
- Google Ads certification preferred
- Experience with GA4 and analytics
- HubSpot and Salesforce knowledge
- Customer acquisition strategies
- Lead generation expertise
- Brand awareness campaigns"""
        
        st.session_state.results = None
        st.session_state.analysis_done = False
        st.rerun()

with col_b3:
    if st.button("🗑️ CLEAR", use_container_width=True, key="clear_button_main"):
        st.session_state.resume = ""
        st.session_state.jd = ""
        st.session_state.results = None
        st.session_state.analysis_done = False
        st.session_state.clear_counter += 1
        st.rerun()

# ============ DISPLAY RESULTS VISUALS ============
if st.session_state.results and st.session_state.analysis_done:
    r = st.session_state.results
    score = r['score']
    
    st.markdown("---")
    st.header("📊 ANALYSIS RESULTS")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if score >= 70:
            st.success(f"### 🎯 EXCELLENT MATCH: {score}%")
        elif score >= 50:
            st.warning(f"### 📈 GOOD MATCH: {score}%")
        else:
            st.error(f"### 💪 NEEDS IMPROVEMENT: {score}%")
        st.progress(score/100)
        st.info(r['interpretation']['message'])
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if 'report_path' in r and Path(r['report_path']).exists():
            with open(r['report_path'], 'r', encoding='utf-8') as f: 
                report_content = f.read()
            st.download_button("📄 Download Text Report", report_content, 
                             file_name="match_report.txt", mime="text/plain", use_container_width=True)
    with col_d2:
        if 'html_report_path' in r and Path(r['html_report_path']).exists():
            with open(r['html_report_path'], 'r', encoding='utf-8') as f: 
                html_content = f.read()
            st.download_button("📊 Download HTML Report", html_content, 
                             file_name="match_report.html", mime="text/html", use_container_width=True)
    
    st.markdown("---")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Match Score", f"{score}%")
    with col_m2:
        total_skills = len(r['matched_skills']) + len(r['missing_skills'])
        st.metric("Skills Matched", f"{len(r['matched_skills'])}/{total_skills if total_skills > 0 else len(r['matched_skills'])}")
    with col_m3:
        total_keywords = len(r['matched_keywords']) + len(r['missing_keywords'])
        st.metric("Keywords Found", f"{len(r['matched_keywords'])}/{total_keywords if total_keywords > 0 else len(r['matched_keywords'])}")
    with col_m4:
        if 'resume_years' in r and 'jd_years' in r and r['jd_years'] > 0:
            exp_match = min(100, (r['resume_years'] / r['jd_years'] * 100)) if r['resume_years'] < r['jd_years'] else 100
            st.metric("Experience Match", f"{exp_match:.0f}%")
    
    st.markdown("---")
    st.subheader("📈 MATCH BREAKDOWN")
    if 'breakdown' in r:
        for category, score_value in r['breakdown'].items():
            col_bar1, col_bar2 = st.columns([1, 3])
            with col_bar1:
                st.write(f"{category.title()}")
            with col_bar2:
                bar_length = int(score_value / 5)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                st.write(f"{bar} {score_value:.1f}%")
    
    st.markdown("---")
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        st.subheader("✅ Matched Skills")
        if r['matched_skills']:
            for skill in sorted(r['matched_skills'])[:15]: 
                st.write(f"• {skill.title()}")
        else: 
            st.info("No skills matched yet")
        
        # Show skill partial matches if any
        if r.get('skill_partial_matches'):
            st.markdown("---")
            st.caption("🔍 **Partial Skill Matches** (similar but not exact):")
            for jd_skill, matched_skill in list(r['skill_partial_matches'].items())[:5]:
                st.caption(f"• '{jd_skill}' → matched as '{matched_skill}'")
    
    with col_sc2:
        st.subheader("❌ Missing Skills")
        if r['missing_skills']:
            for skill in sorted(r['missing_skills'])[:15]: 
                st.write(f"• {skill.title()}")
        else: 
            st.success("All required skills covered!")
    
    st.markdown("---")
    col_kw1, col_kw2 = st.columns(2)
    with col_kw1:
        st.subheader("✅ Matched Keywords")
        if r['matched_keywords']: 
            # Show matched keywords in a grid
            matched_keywords_sorted = sorted(r['matched_keywords'])[:20]
            cols = st.columns(3)
            for idx, keyword in enumerate(matched_keywords_sorted):
                with cols[idx % 3]:
                    st.write(f"• {keyword}")
        else: 
            st.info("No keywords matched")
        
        # Show partial matches if any
        if r.get('partial_matches'):
            st.markdown("---")
            st.caption("🔍 **Partial Keyword Matches** (substring matches):")
            for jd_kw, matched_kw in list(r['partial_matches'].items())[:5]:
                st.caption(f"• '{jd_kw}' → found in '{matched_kw}'")
    
    with col_kw2:
        st.subheader("🔑 Missing Keywords")
        if r['missing_keywords']:
            missing_keywords_sorted = sorted(r['missing_keywords'])[:20]
            cols = st.columns(2)
            for idx, keyword in enumerate(missing_keywords_sorted):
                with cols[idx % 2]:
                    st.write(f"• {keyword}")
        else:
            st.success("All keywords covered!")
        
        # Show semantic matches if any (these are keywords that WERE matched semantically)
        if r.get('semantic_matches'):
            st.markdown("---")
            st.caption("✨ **Semantically Matched Keywords** (conceptually similar):")
            for jd_kw, match_info in list(r['semantic_matches'].items())[:5]:
                if isinstance(match_info, dict):
                    similarity = match_info.get('similarity', 0)
                    matched_to = match_info.get('matched_to', 'unknown')
                    st.caption(f"• '{jd_kw}' → matched to '{matched_to}' (similarity: {similarity:.2f})")
                else:
                    st.caption(f"• '{jd_kw}' → matched to '{match_info}'")
    
    st.markdown("---")
    st.header("🚀 AI-POWERED SUGGESTIONS")
    tab_s1, tab_s2, tab_s3, tab_s4 = st.tabs(["📝 Resume Bullets", "📚 Learning Resources", "⚡ Enhancements", "🤖 ATS Check"])
    
    with tab_s1:
        st.subheader("Add these bullet points to your resume:")
        if r.get('bullet_suggestions'):
            st.markdown(r['bullet_suggestions'])
        else:
            st.info("No bullet suggestions available. Try adding more missing keywords first.")
    
    with tab_s2:
        st.subheader("Learning Resources for Missing Skills:")
        if r.get('skill_recommendations'):
            st.markdown(r['skill_recommendations'])
        else:
            st.info("No skill recommendations available. Great job covering all required skills!")
    
    with tab_s3:
        st.subheader("Resume Enhancement Tips:")
        if r.get('enhancements'):
            st.markdown(r['enhancements'])
        else:
            st.info("No enhancement tips available.")
    
    with tab_s4:
        st.subheader("ATS Compatibility Check:")
        if r.get('ats_check'):
            st.markdown(r['ats_check'])
        else:
            st.info("Run analysis to get ATS compatibility check.")
    
    st.markdown("---")
    st.subheader("📋 3-STEP ACTION PLAN")
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        st.info("1️⃣ IMMEDIATE (5 min)")
        if r['missing_skills']:
            st.write(f"• Add {min(3, len(r['missing_skills']))} missing skill(s) to your resume")
        elif r['missing_keywords']:
            st.write(f"• Add {min(3, len(r['missing_keywords']))} missing keyword(s) to your resume")
        else:
            st.write("• Review your resume for formatting and clarity")
    
    with col_act2:
        st.info("2️⃣ TODAY (20 min)")
        if r['missing_keywords']:
            st.write(f"• Incorporate {min(5, len(r['missing_keywords']))} keywords into experience bullets")
        elif r.get('semantic_matches'):
            st.write("• Strengthen semantically matched keywords with concrete examples")
        else:
            st.write("• Quantify 2-3 achievements with metrics")
    
    with col_act3:
        st.info("3️⃣ THIS WEEK (1 hour)")
        if r['missing_skills']:
            st.write("• Build a mini-project or take a course in a missing skill area")
        else:
            st.write("• Update LinkedIn profile with matched keywords")
            st.write("• Network with professionals in target role")
    
    # Show interpretation action at the bottom
    st.markdown("---")
    st.info(f"💡 **Recommendation:** {r['interpretation']['action']}")

# ============ SIDEBAR MANAGEMENT ============
with st.sidebar:
    st.header("👤 ACCOUNT")
    st.markdown("---")
    
    if not st.session_state.user:
        tab_ac1, tab_ac2 = st.tabs(["LOGIN", "SIGN UP"])
        
        with tab_ac1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("LOGIN", use_container_width=True):
                    if email and password:
                        st.session_state.user = email
                        history = load_analysis_history(email)
                        st.session_state.analysis_history = []
                        for h in history:
                            # Parse semantic matches from JSON
                            semantic_matches = {}
                            try:
                                if h[11]:  # semantic_matches column
                                    semantic_matches = json.loads(h[11])
                            except:
                                pass
                            
                            st.session_state.analysis_history.append({
                                'id': h[0], 
                                'timestamp': h[1], 
                                'score': h[2], 
                                'job_title': h[3] or 'Unknown', 
                                'report_path': h[5], 
                                'html_report_path': h[6],
                                'semantic_matches': semantic_matches
                            })
                        st.success(f"Welcome back, {email.split('@')[0]}!")
                        st.rerun()
        
        with tab_ac2:
            with st.form("signup_form"):
                email = st.text_input("Email")
                name = st.text_input("Full Name")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    if email and name and password:
                        # In production, hash password and save to DB
                        st.session_state.user = email
                        st.session_state.analysis_history = []
                        st.success("Account created successfully!")
                        st.rerun()
        
        if st.button("👤 GUEST MODE", use_container_width=True):
            st.session_state.user = "guest"
            st.rerun()
    
    else:
        username = st.session_state.user.split('@')[0] if '@' in st.session_state.user else 'Guest'
        st.success(f"👋 Logged in as **{username}**")
        
        if st.session_state.user != "guest" and st.session_state.analysis_history:
            st.markdown("---")
            st.subheader("📜 RECENT ANALYSES")
            for analysis in st.session_state.analysis_history[:5]:
                with st.expander(f"📋 {analysis['job_title']} - {analysis['score']}%"):
                    st.write(f"📅 {analysis['timestamp']}")
                    if analysis.get('semantic_matches'):
                        st.caption(f"✨ {len(analysis['semantic_matches'])} semantic matches found")
                    if st.button("Load", key=f"load_{analysis['id']}"):
                        st.info("Load functionality coming soon")
        
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            st.session_state.user = None
            st.session_state.analysis_history = []
            st.session_state.results = None
            st.session_state.analysis_done = False
            st.rerun()
    
    st.markdown("---")
    st.header("📌 HOW TO USE")
    st.markdown("""
    1. **Paste or upload** your resume
    2. **Paste or upload** job description  
    3. Click **ANALYZE MATCH**
    4. Review your **AI-powered suggestions**
    5. Download **detailed reports**
    6. History saves automatically for logged-in users
    
    ---
    
    ### 🆕 Enhanced Features
    - **Semantic matching** finds conceptually similar keywords
    - **Partial matching** catches variations of skills
    - **Phrase detection** captures multi-word keywords
    - **Dynamic weights** adjust based on content
    """)
    st.markdown("---")
    st.caption("© 2026 ResumeAlign - Intelligent Resume Matching")

# ============ FOOTER ============
st.markdown("---")
st.caption("💡 **Pro tip:** Log in to save your analysis history and track your progress over time!")