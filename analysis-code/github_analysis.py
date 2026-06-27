import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

repo = "openai/codex"

url = f"https://api.github.com/repos/{repo}/contributors"

response = requests.get(url, headers=headers)

contributors = response.json()

rows = []

for user in contributors:
    rows.append({
        "login": user["login"],
        "id": user["id"],
        "contributions": user["contributions"]
    })

df = pd.DataFrame(rows)

print(df)

df.to_csv("../output/codex_contributors.csv", index=False)