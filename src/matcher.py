from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def compute_match(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([clean(resume_text), clean(job_description)])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 2)
