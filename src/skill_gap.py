# src/skill_gap.py - EXPANDED VERSION
import re

# Much larger skill database
COMMON_SKILLS = {
    # Programming Languages
    'programming': [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
        'kotlin', 'go', 'rust', 'typescript', 'html', 'css', 'sql', 'nosql'
    ],
    
    # Frameworks & Libraries
    'frameworks': [
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js',
        'express', 'jquery', 'bootstrap', 'tailwind', 'tensorflow', 'pytorch'
    ],
    
    # Databases
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis',
        'elasticsearch', 'dynamodb', 'cassandra', 'mariadb'
    ],
    
    # Cloud & DevOps
    'cloud': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
        'github', 'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux'
    ],
    
    # Data Science
    'data_science': [
        'machine learning', 'data analysis', 'data visualization', 'statistics',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tableau',
        'power bi', 'excel', 'r', 'spss', 'sas'
    ],
    
    # Business Skills
    'business': [
        'project management', 'agile', 'scrum', 'leadership', 'communication',
        'teamwork', 'problem solving', 'critical thinking', 'time management',
        'presentation', 'negotiation', 'stakeholder management'
    ],
    
    # Soft Skills
    'soft_skills': [
        'collaboration', 'adaptability', 'creativity', 'attention to detail',
        'organization', 'prioritization', 'conflict resolution', 'mentoring'
    ],
    
    # Marketing
    'marketing': [
        'seo', 'sem', 'social media', 'content marketing', 'email marketing',
        'google analytics', 'adwords', 'facebook ads', 'copywriting', 'branding'
    ],
    
    # Design
    'design': [
        'ui design', 'ux design', 'graphic design', 'photoshop', 'illustrator',
        'figma', 'sketch', 'adobe xd', 'invision', 'wireframing', 'prototyping'
    ],
    
    # Office Tools
    'office': [
        'microsoft word', 'microsoft excel', 'microsoft powerpoint',
        'google docs', 'google sheets', 'google slides', 'slack', 'teams',
        'zoom', 'asana', 'trello', 'jira', 'confluence', 'notion'
    ]
}

def extract_skills(text):
    """
    Extract skills from ANY job description or resume with improved detection
    """
    text = text.lower()
    found_skills = set()
    
    # Flatten all skills into one list
    all_skills = []
    for category in COMMON_SKILLS.values():
        all_skills.extend(category)
    
    # Check for each skill
    for skill in all_skills:
        if ' ' in skill:  # Multi-word skill
            if re.search(rf'\b{skill}\b', text):
                found_skills.add(skill)
        else:  # Single word skill
            if re.search(rf'\b{skill}\b', text):
                found_skills.add(skill)
    
    # Also look for common skill indicators
    skill_indicators = [
        r'skilled in (\w+)',
        r'expertise in (\w+)',
        r'proficient in (\w+)',
        r'experience with (\w+)',
        r'knowledge of (\w+)',
        r'familiar with (\w+)',
        r'working knowledge of (\w+)',
        r'hands-on experience with (\w+)'
    ]
    
    for pattern in skill_indicators:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, str) and len(match) > 2:
                found_skills.add(match)
    
    return found_skills