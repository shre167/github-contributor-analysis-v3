import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Personal Access Token
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("❌ GITHUB_TOKEN not found in .env file")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Read contributors CSV
contributors_file = "../output/codex_contributors.csv"

try:
    contributors = pd.read_csv(contributors_file)
except FileNotFoundError:
    raise FileNotFoundError(
        f"❌ Could not find {contributors_file}. Run github_analysis.py first."
    )

profiles = []

print(f"Fetching profiles for {len(contributors)} contributors...\n")

for index, row in contributors.iterrows():

    login = row["login"]

    url = f"https://api.github.com/users/{login}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        user = response.json()

        profiles.append({
            "github_login": user.get("login"),
            "github_id": user.get("id"),
            "name": user.get("name"),
            "company": user.get("company"),
            "bio": user.get("bio"),
            "location": user.get("location"),
            "email": user.get("email"),
            "blog": user.get("blog"),
            "twitter_username": user.get("twitter_username"),
            "public_repos": user.get("public_repos"),
            "followers": user.get("followers"),
            "following": user.get("following"),
            "created_at": user.get("created_at"),
            "html_url": user.get("html_url")
        })

        print(f"✅ {login}")

    else:
        print(f"❌ Failed to fetch {login} ({response.status_code})")

# Convert to DataFrame
profiles_df = pd.DataFrame(profiles)

# Create output directory if it doesn't exist
os.makedirs("../output", exist_ok=True)

# Save CSV
output_file = "../output/profiles.csv"
profiles_df.to_csv(output_file, index=False)

print("\n--------------------------------")
print(f"✅ Saved {len(profiles_df)} profiles")
print(f"📄 Output: {output_file}")
print("--------------------------------")

print("\nFirst 5 rows:\n")
print(profiles_df.head())