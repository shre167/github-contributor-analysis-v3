import os
import pandas as pd
from dotenv import load_dotenv
from apify_client import ApifyClient

# ==========================
# Load API Token
# ==========================

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    raise ValueError("❌ APIFY_TOKEN not found in .env")

client = ApifyClient(APIFY_TOKEN)

# ==========================
# Read contributor data
# ==========================

df = pd.read_csv("../output/classified_contributors.csv")

# Merge contributions if available
contributors = pd.read_csv("../output/codex_contributors.csv")

df = df.merge(
    contributors[["login", "contributions"]],
    left_on="github_login",
    right_on="login",
    how="left"
)

df.drop(columns=["login"], inplace=True)

df = df.sort_values("contributions", ascending=False)

TOP_N = 20

df = df.head(TOP_N).copy()

linkedin_urls = []

# ==========================
# Search LinkedIn
# ==========================

for _, row in df.iterrows():

    name = row["name"]

    if pd.isna(name):
        name = row["github_login"]

    query = f'"{name}" site:linkedin.com/in'

    print(f"\nSearching: {query}")

    run_input = {
        "queries": query,
        "maxPagesPerQuery": 1
    }

    try:

        run = client.actor("apify/google-search-scraper").call(
            run_input=run_input
        )

        # New Apify client
        dataset = client.dataset(run.default_dataset_id)

        items = list(dataset.iterate_items())

        linkedin = "Unknown"

        for item in items:

            if "organicResults" not in item:
                continue

            for result in item["organicResults"]:

                url = result.get("url", "")

                if "linkedin.com/in/" in url.lower():
                    linkedin = url
                    break

            if linkedin != "Unknown":
                break

        print("Found:", linkedin)

        linkedin_urls.append(linkedin)

    except Exception as e:

        print("ERROR:", e)

        linkedin_urls.append("Unknown")

# ==========================
# Save
# ==========================

df["linkedin_url"] = linkedin_urls

output = "../output/linkedin_results.csv"

df.to_csv(output, index=False)

print("\n==========================")
print("Finished!")
print("==========================")

print(df[
    [
        "github_login",
        "name",
        "linkedin_url"
    ]
])

print(f"\nSaved to {output}")