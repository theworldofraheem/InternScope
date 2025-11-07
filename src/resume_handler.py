# src/resume_handler.py
import os
import fitz  # PyMuPDF

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
