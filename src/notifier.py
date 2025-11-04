# src/notifier.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def notify_discord(job, score):
    """
    Sends a job match alert to your Discord channel using a webhook.
    """
    if not WEBHOOK_URL:
        print("No Discord webhook URL found in .env")
        return

    title = job.get("title", "Untitled Job")
    company = job.get("company", "Unknown Company")
    link = job.get("link", "")
    location = job.get("location", "N/A")
    description = job.get("description", "No description available.")
    source = job.get("source", "Unknown Source")

    color = 0x2ecc71 if score >= 85 else (0xf1c40f if score >= 70 else 0xe74c3c)

    embed = {
        "title": f"🚀 {title}",
        "url": link,
        "color": color,
        "fields": [
            {"name": "Company", "value": company, "inline": True},
            {"name": "Location", "value": location, "inline": True},
            {"name": "Source", "value": source, "inline": True},
            {"name": "Match Score", "value": f"**{score}%**", "inline": False},
        ],
        "footer": {
            "text": "InternScope Job Monitor",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/10307/10307950.png"
        }
    }

    data = {"embeds": [embed]}

    try:
        resp = requests.post(WEBHOOK_URL, json=data)
        if resp.status_code == 204:
            print(f"Sent notification for {company}: {title} ({score}%)")
        else:
            print(f"Discord webhook failed with status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

if __name__ == "__main__":
    fake_job = {
        "title": "Software Developer",
        "company": "Test Company",
        "link": "https://example.com/job",
        "location": "Remote",
        "description": "A sample job posting to test Discord integration.",
        "source": "Manual Test"
    }
    notify_discord(fake_job, 88)

