from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load a compact, fast model for sentence embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

def clean(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def compute_match(resume_text: str, job_text: str) -> float:
    
    #Returns a similarity score (0–100) between résumé and job posting using semantic embeddings.
    
    if not resume_text or not job_text:
        return 0.0

    embeddings = model.encode([resume_text, job_text], convert_to_numpy=True)
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 2)

def hybrid_match_score(resume_text, job_text, resume_skills):
    #Looks at semantic similarity + skill overlap to produce a better score.
    
    sem_score = compute_match(resume_text, job_text)  # 0–100 range

    # Bonus: count overlap between extracted skills and job posting
    overlap = sum(kw in job_text.lower() for kw in resume_skills)
    skill_boost = min(overlap * 5, 20)  # up to +20 points

    # Penalize senior roles
    senior_terms = ["senior", "lead", "manager", "director", "principal"]
    if any(t in job_text.lower() for t in senior_terms):
        sem_score -= 25

    final_score = min(max(sem_score + skill_boost, 0), 100)
    return round(final_score, 2)
