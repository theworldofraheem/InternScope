import os
import time
import fitz 
import json
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from storage import load_seen_jobs
from storage import save_seen_jobs
from scraper import fetch_lever_jobs, fetch_indeed_jobs, gather_all_jobs
from matcher import compute_match
from notifier import notify_discord
from resume_handler import get_resume_text 
from logger import setup_logger

# --- Load configuration ---
logger = setup_logger() 

with open("src/config.json") as f:
    CONFIG = json.load(f)

COMPANIES = CONFIG["companies"]
CHECK_INTERVAL_HOURS = CONFIG["check_interval_hours"]
MATCH_THRESHOLD = CONFIG["match_threshold"]
DEBUG_MODE = CONFIG["debug_mode"]

# --- Load token from .env file ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Discord intents configuration ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variable to hold uploaded resume text
resume_text = ""

# --- Function: Extract text from PDF ---
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# --- Slash command: upload resume ---
@bot.tree.command(name="upload_resume", description="Upload your resume PDF for analysis.")
async def upload_resume(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Please upload your resume PDF as a file attachment within 5 minutes."
    )

    def check(msg):
        return msg.author == interaction.user and msg.attachments

    try:
        msg = await bot.wait_for("message", timeout=300.0, check=check)
        attachment = msg.attachments[0]

        if not attachment.filename.lower().endswith(".pdf"):
            await interaction.followup.send("Please upload a `.pdf` file.")
            return

        os.makedirs("src/data", exist_ok=True)
        file_path = f"src/data/{attachment.filename}"
        await attachment.save(file_path)

        global resume_text
        resume_text = extract_text_from_pdf(file_path)
        await interaction.followup.send(f"Resume '{attachment.filename}' uploaded successfully!")
    except Exception as e:
        await interaction.followup.send(f"Upload failed: {e}")

# --- Slash command: analyze resume ---
@bot.tree.command(name="analyze_resume", description="Analyze your uploaded resume for key skills.")
async def analyze_resume(interaction: discord.Interaction):
    global resume_text
    if not resume_text:
        await interaction.response.send_message(" No resume uploaded yet. Use `/upload_resume` first.")
        return

    # Basic keyword-based check
    keywords = ["python", "java", "sql", "data", "machine learning", "flask", "react"]
    strengths = [kw for kw in keywords if kw in resume_text.lower()]
    missing = [kw for kw in keywords if kw not in strengths]

    feedback = (
        f"**Found skills:** {', '.join(strengths) or 'None detected'}\n"
        f"**Missing skills:** {', '.join(missing) or 'None!'}"
    )

    await interaction.response.send_message(feedback)
# --- Slash command: update resume ---
@bot.tree.command(name="update_resume", description="Replace your existing resume with a new one.")
async def update_resume(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Please upload your updated resume PDF within 5 minutes."
    )

    def check(msg):
        return msg.author == interaction.user and msg.attachments

    try:
        msg = await bot.wait_for("message", timeout=300.0, check=check)
        attachment = msg.attachments[0]

        if not attachment.filename.lower().endswith(".pdf"):
            await interaction.followup.send("Please upload a `.pdf` file.")
            return

        os.makedirs("src/data", exist_ok=True)
        file_path = f"src/data/{attachment.filename}"

        # Delete old resume if it exists
        old_files = [f for f in os.listdir("src/data") if f.lower().endswith(".pdf")]
        for f in old_files:
            os.remove(os.path.join("src/data", f))

        await attachment.save(file_path)
        global resume_text
        resume_text = extract_text_from_pdf(file_path)

        await interaction.followup.send(
            f"Your resume has been successfully **updated** to `{attachment.filename}`!"
        )
    except Exception as e:
        await interaction.followup.send(f"Update failed: {e}")

# --- Slash command: delete resume ---
@bot.tree.command(name="delete_resume", description="Delete your uploaded resume.")
async def delete_resume(interaction: discord.Interaction):
    deleted = False
    if os.path.exists("src/data"):
        for f in os.listdir("src/data"):
            if f.lower().endswith(".pdf"):
                os.remove(os.path.join("src/data", f))
                deleted = True

    global resume_text
    resume_text = ""
    msg = "Your resume has been deleted." if deleted else " No resume found to delete."
    await interaction.response.send_message(msg)

@tasks.loop(hours=CHECK_INTERVAL_HOURS)
async def job_monitor():
    logger.info("Running scheduled job check...")
    seen = load_seen_jobs()
    resume_text = get_resume_text()
    jobs = gather_all_jobs()
    new_seen = set(seen)

    for job in jobs:
        if job['link'] not in seen:
            desc = job.get("description", "")
            score = compute_match(resume_text, job["title"] + " " + desc)
            if score >= MATCH_THRESHOLD:
                notify_discord(job, score)
                logger.info(f"New job found: {job['title']} ({score}%)")
            
            new_seen.add(job["link"])

    save_seen_jobs(new_seen)
    print("Job check complete.")



# --- Event: on_ready ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    job_monitor.start()     # start the background loop
    print(f"Logged in as {bot.user}")


# --- Run the bot ---
bot.run(TOKEN)
