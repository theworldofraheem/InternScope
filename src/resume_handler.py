# src/resume_handler.py
import os
import fitz  
import re
def get_resume_text():
    """Return text from the most recently uploaded resume PDF, or '' if none found."""
    data_dir = "src/data"
    if not os.path.exists(data_dir):
        return ""

    for file in os.listdir(data_dir):
        if file.lower().endswith(".pdf"):
            with fitz.open(os.path.join(data_dir, file)) as pdf:
                return "".join(page.get_text() for page in pdf)

    return ""

def is_resume_text(text):
    keywords = ["experience", "education", "skills", "projects", "contact", "summary"]
    matches = sum(1 for k in keywords if k in text.lower())
    return matches >= 2



def extract_resume_skills(text: str):
    """Extract a skill fingerprint from the resume text."""
    skill_keywords = [
        "python","java","c++","c","sql","javascript","typescript","react","node","flask",
        "django","html","css","pandas","numpy","tensorflow","pytorch",
        "machine learning","deep learning","ai","cloud","aws","azure","docker","git"
    ]
    skills = [kw for kw in skill_keywords if re.search(rf"\\b{kw}\\b", text, re.I)]
    return list(set(skills))
