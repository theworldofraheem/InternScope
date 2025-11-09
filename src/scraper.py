import requests
import feedparser
import logging



INTERNSHIP_KEYWORDS = [
    "intern", "internship", "co-op", "co op", "coop",
    "student", "work term","work-term","workterm", "placement", 
    "undergraduate", "Software", "Developer","jr", "junior", 
    "Computer Science","Computer-Science","CS","datascience",
    "Data science","Data-science","tech","Python", "Java","C++", "C#",
    "react", "git", "machine learning", "artificial intelligence", "AI",
    "cloud", "aws", "azure", "docker", "git-hub", "github"
]

def is_internship_posting(text: str) -> bool:
    return any(kw in text.lower() for kw in INTERNSHIP_KEYWORDS)

# --- 1. Lever-hosted companies ---
LEVER_COMPANIES = [
    "verafin", "colabsoftware","colab software", "colab-software"
    "stripe", "datadog", "shopify", "BMO","Lancey",
    "Welathsimple", "Microsoft", "LockheedMartin", "MorganStanley",
    "TD Bank", "TD-Bank","TDBank", "Nokia", "Shopify",
    "Mastercard","Intel", "Cisco", "Remitly", "Amazon", "Siemens", 
    "IBM", "Autodesk", "lyft", "RBC", "google","pinterest", "cgi",
    "instacart", "Avalon-holographics","Avalon Holographics","AvalonHolographics", "square"
    ]

logger = logging.getLogger("InternScope")
def fetch_lever_jobs():
    jobs = []
    for company in LEVER_COMPANIES:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                for post in resp.json():
                    text_fields = " ".join([
                        post.get("text", ""),
                        post.get("descriptionPlain", ""),
                        post.get("categories", {}).get("team", "")
                    ])
                    if not is_internship_posting(text_fields):
                        continue
                    jobs.append({
                        "title": post.get("text", ""),
                        "company": company.capitalize(),
                        "link": post.get("hostedUrl"),
                        "location": post.get("categories", {}).get("location", ""),
                        "description": post.get("descriptionPlain", ""),
                        "source": "Lever"
                    })
        except Exception as e:
            logger.warning(f"[{company}] Lever fetch failed: {e}")
    return jobs

# --- 2. Indeed RSS feed ---
def fetch_indeed_jobs(query="computer+science+canada"):
    url = f"https://www.indeed.com/rss?q={query}"
    feed = feedparser.parse(url)
    jobs = []
    for entry in feed.entries:
        if not is_internship_posting(entry.title + " " + entry.summary):
            continue
        jobs.append({
            "title": entry.title,
            "company": "Indeed",
            "link": entry.link,
            "location": "",
            "description": entry.summary,
            "source": "Indeed"
        })
    return jobs

# --- 3. Workday-based postings (common format for Amazon, IBM, etc.) ---
def fetch_workday_jobs(base_url):
    # Example base_url: 'https://amazonrobotics.wd5.myworkdayjobs.com/en-US/StudentPrograms'
    jobs = []
    try:
        resp = requests.get(base_url, timeout=10)
        if resp.ok:
            text = resp.text
            if not is_internship_posting(text):
                return jobs
            jobs.append({
                "title": "Workday Internship Listing",
                "company": base_url.split(".")[0].replace("https://", "").capitalize(),
                "link": base_url,
                "location": "",
                "description": "Workday job page (parse more details later)",
                "source": "Workday"
            })
    except Exception as e:
        logger.warning(f"[Workday] fetch failed: {e}")
    return jobs

def fetch_greenhouse_jobs(company):
    """Pull internship postings from Greenhouse boards."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    jobs = []
    try:
        resp = requests.get(url, timeout=10)
        if not resp.ok:
            return jobs
        data = resp.json()
        for post in data.get("jobs", []):
            text = (post.get("title", "") + " " +
                    post.get("content", "") + " " +
                    post.get("location", {}).get("name", ""))
            if not is_internship_posting(text):
                continue
            jobs.append({
                "title": post.get("title", ""),
                "company": company.capitalize(),
                "link": post.get("absolute_url"),
                "location": post.get("location", {}).get("name", ""),
                "description": post.get("content", ""),
                "source": "Greenhouse"
            })
    except Exception as e:
        logger.warning(f"[Greenhouse] {company} fetch failed: {e}")
    return jobs


def fetch_indeed_query(query: str):
    """Fetch Indeed postings for a custom search query."""
    url = f"https://www.indeed.com/rss?q={query.replace(' ', '+')}"
    feed = feedparser.parse(url)
    jobs = []
    for entry in feed.entries:
        text = entry.title + " " + entry.summary
        if not is_internship_posting(text):
            continue
        jobs.append({
            "title": entry.title,
            "company": "Indeed",
            "link": entry.link,
            "location": "",
            "description": entry.summary,
            "source": "Indeed"
        })
    logger.info(f"Fetched {len(jobs)} Indeed results for '{query}'.")
    return jobs

# --- Combine all sources ---
def gather_all_jobs():
    all_jobs = []
    all_jobs.extend(fetch_lever_jobs())
    all_jobs.extend(fetch_indeed_jobs())
    # add Workday if needed
    # all_jobs.extend(fetch_workday_jobs("https://amazonrobotics.wd5.myworkdayjobs.com/en-US/StudentPrograms"))
    return all_jobs

if __name__ == "__main__":
    jobs = gather_all_jobs()
    logger.info(f"Found {len(jobs)} internship postings.")
    for j in jobs[:5]:
        logger.info(f"- {j['company']}: {j['title']} ({j['source']})")

