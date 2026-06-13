import re

# =====================================================
# BASE SKILLS DATABASE
# =====================================================

BASE_SKILLS = {

    # Programming
    "python",
    "sql",
    "java",
    "javascript",
    "c++",
    "c#",
    "r",

    # Analytics
    "tableau",
    "power bi",
    "excel",
    "pandas",
    "numpy",

    # Cloud
    "aws",
    "azure",
    "gcp",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",

    # DevOps
    "docker",
    "kubernetes",
    "git",

    # Marketing
    "seo",
    "sem",
    "google ads",
    "google analytics",
    "ga4",
    "hubspot",
    "salesforce",
    "meta",
    "linkedin",
    "email marketing",
    "cro",
    "conversion rate optimization",
    "looker studio"
}

# =====================================================
# ALIASES
# =====================================================

ALIASES = {

    "powerbi": "power bi",
    "power_bi": "power bi",

    "google analytics 4": "ga4",

    "reactjs": "react",
    "node.js": "nodejs",

    "machine_learning": "machine learning",
    "deep_learning": "deep learning",

    "business_intelligence": "business intelligence",

    "cplusplus": "c++",
    "csharp": "c#",

    "a/b testing": "ab testing",
    "a b testing": "ab testing"
}

# =====================================================
# NORMALIZE
# =====================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    for old, new in ALIASES.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# =====================================================
# EXTRACT JD SKILLS DYNAMICALLY
# =====================================================

def extract_dynamic_skills(text):

    text = normalize_text(text)

    skills = set()

    patterns = [

        r"google ads",
        r"google analytics",
        r"ga4",
        r"looker studio",
        r"hubspot",
        r"salesforce",
        r"seo",
        r"sem",
        r"meta",
        r"linkedin",
        r"email marketing",
        r"cro",
        r"conversion rate optimization",
        r"ab testing",
        r"customer acquisition",
        r"campaign strategy",
        r"budget management",
        r"team management",

        r"python",
        r"sql",
        r"tableau",
        r"power bi",
        r"aws",
        r"azure",
        r"docker",
        r"kubernetes"
    ]

    for pattern in patterns:

        if re.search(rf"\b{re.escape(pattern)}\b", text):
            skills.add(pattern)

    return skills

# =====================================================
# EXTRACT SKILLS
# =====================================================

def extract_skills(text):

    text = normalize_text(text)

    found = set()

    for skill in BASE_SKILLS:

        if re.search(
            rf"\b{re.escape(skill)}\b",
            text
        ):
            found.add(skill)

    dynamic = extract_dynamic_skills(text)

    return found.union(dynamic)

# =====================================================
# MATCH
# =====================================================

def calculate_skill_match(
    resume_text,
    jd_text
):

    resume_skills = extract_skills(
        resume_text
    )

    jd_skills = extract_skills(
        jd_text
    )

    matched = (
        resume_skills &
        jd_skills
    )

    missing = (
        jd_skills -
        resume_skills
    )

    score = 0

    if len(jd_skills) > 0:

        score = round(
            len(matched)
            / len(jd_skills)
            * 100,
            2
        )

    return {

        "score": score,

        "matched":
            sorted(
                list(matched)
            ),

        "missing":
            sorted(
                list(missing)
            ),

        "resume_skills":
            sorted(
                list(resume_skills)
            ),

        "jd_skills":
            sorted(
                list(jd_skills)
            )
    }

# =====================================================
# PRIORITY SKILLS
# =====================================================

def get_priority_missing_skills(
    resume_text,
    jd_text,
    limit=10
):

    result = calculate_skill_match(
        resume_text,
        jd_text
    )

    return result["missing"][:limit]

# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    resume = """
    Digital Marketing Manager with SEO,
    SEM, GA4, HubSpot, Salesforce,
    Google Ads and CRO.
    """

    jd = """
    Looking for SEO, SEM, GA4,
    HubSpot, Salesforce,
    Google Ads, CRO and Meta.
    """

    result = calculate_skill_match(
        resume,
        jd
    )

    print(result)