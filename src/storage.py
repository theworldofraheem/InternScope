import json, os

DATA_FILE = "src/data/seen_jobs.json"

def load_seen_jobs():
    """Return a set of already-seen job links, or an empty set if file missing/invalid."""
    if not os.path.exists(DATA_FILE):
        return set()
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return set()
            return set(json.loads(content))
    except (json.JSONDecodeError, ValueError):
        # file exists but has invalid/empty JSON
        return set()

def save_seen_jobs(seen):
    os.makedirs("src/data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(list(seen), f)
