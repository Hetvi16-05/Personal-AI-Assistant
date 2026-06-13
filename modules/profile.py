import json
import os

PROFILE_FILE = "data/profile.json"

DEFAULT_PROFILE = {
    "name": None,
    "goal": None,
    "interests": [],
    "study_topics": [],
    "notes": []
}

def load_profile():
    if not os.path.exists(PROFILE_FILE):
        return DEFAULT_PROFILE.copy()

    with open(PROFILE_FILE, "r") as f:
        data = json.load(f)

    # Merge with defaults to handle missing keys
    profile = DEFAULT_PROFILE.copy()
    profile.update(data)
    return profile

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def update_profile(key, value):
    profile = load_profile()
    if key in ("interests", "study_topics", "notes"):
        if value not in profile[key]:
            profile[key].append(value)
    else:
        profile[key] = value
    save_profile(profile)

def get_profile():
    return load_profile()

def get_profile_summary():
    profile = load_profile()
    lines = []

    if profile.get("name"):
        lines.append(f"👤 **Name:** {profile['name']}")
    if profile.get("goal"):
        lines.append(f"🎯 **Goal:** {profile['goal']}")
    if profile.get("interests"):
        lines.append(f"💡 **Interests:** {', '.join(profile['interests'])}")
    if profile.get("study_topics"):
        lines.append(f"📚 **Study Topics:** {', '.join(profile['study_topics'])}")
    if profile.get("notes"):
        lines.append(f"📝 **Notes:** {', '.join(profile['notes'])}")

    if not lines:
        return None
    return "\n".join(lines)
