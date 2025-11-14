# InternScope
**Your personal internship radar** automatically tracks personal internship postings, extracts requirements, and ranks how well your résumé matches each job.

---

## Overview
InternScope is a Python-based automation tool that continuously monitors job boards and company career pages for **CS, Data Science, and Software Engineering internships**.  
When new postings appear, it:
1. Detects and parses new listings  
2. Extracts key requirements & skills  
3. Compares them to your résumé using NLP  
4. Sends you a notification with your **match score**

---

## Tech Stack

**Language** Python 3.10+ 
**Scraping / APIs:**  `requests`, `BeautifulSoup4`, `feedparser`
**Matching Engine:**  `scikit-learn`, `sentence-transformers`, `nltk` 
**Notifications:** Discord Webhooks / Telegram / Email (via SMTP) 
**Scheduler:** `cron`, GitHub Actions, or local task scheduler 

---

## Features
Search across multiple job sites (Indeed, Workday, Lever, etc.)
Extract job requirements and key qualifications
Calculate **resume-to-job similarity scores**
Send smart notifications (only when relevant)
Keep history of past postings
Configurable keywords, thresholds, and frequency

---

## Installation

```bash
git clone https://github.com/<your-username>/InternScope.git
cd InternScope/src
pip install -r requirements.txt

