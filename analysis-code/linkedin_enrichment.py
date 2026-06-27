import requests
import pandas as pd
import time
import re
import sys

# =========================================================
# CONFIG
# =========================================================
API_KEY = "3c83b896-b3f3-4272-be77-26c6d3513643"
DATASET_ID = "gd_l1viktl72bvl7bjuj0"

# Target explicit JSON endpoint configuration
API_URL = f"https://api.brightdata.com/datasets/v3/scrape?dataset_id={DATASET_ID}&format=json"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

CURRENT_YEAR = 2026

# =========================================================
# LOAD DATA
# =========================================================
try:
    df = pd.read_csv("../output/dataset.csv")
except FileNotFoundError:
    print("dataset.csv not found")
    sys.exit(1)

df = df[df["linkedin_url"].notna()]
df["linkedin_url"] = df["linkedin_url"].astype(str)
df = df[df["linkedin_url"].str.contains("linkedin.com")].reset_index(drop=True)

# =========================================================
# NORMALIZE COMPANY
# =========================================================
def normalize_company(name):
    if not name or not isinstance(name, str):
        return "Unknown"

    n = name.lower()

    if "openai" in n:
        return "OpenAI"
    if "google" in n:
        return "Google"
    if "anthropic" in n:
        return "Anthropic"
    if "xai" in n:
        return "xAI"

    return name.strip().title()

# =========================================================
# TENURE CALCULATION (FIXED FOR CURRENT JOB VARIATIONS)
# =========================================================
def extract_tenure(experiences):
    if not isinstance(experiences, list) or len(experiences) == 0:
        return "Unknown"

    # Bright Data lists profiles chronologically; index 0 is the current/most recent job
    current_job = experiences[0]
    if not isinstance(current_job, dict):
        return "Unknown"

    # Fallback cascade to capture where the start date is defined
    start_date = current_job.get("start_date") or current_job.get("started_on") or current_job.get("start")

    # CASE 1: Nested JSON dictionary structure -> {"year": 2023, "month": 5}
    if isinstance(start_date, dict):
        y = start_date.get("year")
        if y:
            try:
                return max(0, CURRENT_YEAR - int(y))
            except (ValueError, TypeError):
                pass

    # CASE 2: ISO String formats -> "2023-05-15" or raw year strings
    if isinstance(start_date, str):
        match = re.search(r"(20\d{2})", start_date)
        if match:
            return max(0, CURRENT_YEAR - int(match.group(1)))

    # CASE 3: Text fallback parsing across description or period strings
    for alternative_field in ["time_period", "description", "title_raw"]:
        text_val = current_job.get(alternative_field)
        if isinstance(text_val, str):
            match = re.search(r"(20\d{2})", text_val)
            if match:
                return max(0, CURRENT_YEAR - int(match.group(1)))

    return "Unknown"

# =========================================================
# SCRAPER
# =========================================================
def scrape_linkedin(url):

    def safe():
        return {
            "employer_inferred": "Unknown",
            "tenure": "Unknown",
            "confidence": "Low"
        }

    if not isinstance(url, str) or "linkedin.com" not in url:
        return safe()

    # FIX: Root layout array mapping required by Bright Data endpoint specs
    payload = [{"url": url}]

    try:
        res = requests.post(API_URL, json=payload, headers=headers, timeout=90)

        if res.status_code != 200:
            print("API ERROR:", res.status_code, res.text[:150])
            return safe()

        data = res.json()

        # Handle fallback if endpoint switches to background snapshot jobs dynamically
        if isinstance(data, dict) and ("snapshot_id" in data or "id" in data):
            print(f"  Note: Request generated background tracking ID instead of immediate data array.")
            return safe()

        if not isinstance(data, list) or len(data) == 0:
            return safe()

        profile = data[0] if isinstance(data[0], dict) else {}

        # =====================================================
        # EMPLOYER EXTRACTION
        # =====================================================
        employer = "Unknown"

        cc = profile.get("current_company")
        if isinstance(cc, dict):
            employer = cc.get("name", "Unknown")
        elif isinstance(cc, str):
            employer = cc

        if employer == "Unknown":
            exp = profile.get("experiences") or profile.get("positions") or []
            if isinstance(exp, list) and len(exp) > 0:
                job = exp[0]
                if isinstance(job, dict):
                    employer = job.get("company") or job.get("company_name") or "Unknown"

        employer = normalize_company(employer)

        # =====================================================
        # TENURE EXTRACTION (FIXED ROUTING EFFECTED HERE)
        # =====================================================
        experiences = profile.get("experiences") or profile.get("positions") or profile.get("positions_grouped")
        tenure = extract_tenure(experiences)

        # =====================================================
        # OUTPUT
        # =====================================================
        return {
            "employer_inferred": employer,
            "tenure": tenure,
            "confidence": "High" if employer != "Unknown" else "Low"
        }

    except Exception as e:
        print("Exception encountered:", e)
        return safe()

# =========================================================
# RUN PIPELINE
# =========================================================
employers = []
tenures = []
confidences = []

print(f"Processing {len(df)} profiles...\n")

for i, row in df.iterrows():

    url = row["linkedin_url"]
    result = scrape_linkedin(url)

    # Use dict.get to defend against accidental KeyErrors if something drops
    employers.append(result.get("employer_inferred", "Unknown"))
    tenures.append(result.get("tenure", "Unknown"))
    confidences.append(result.get("confidence", "Low"))

    print(f"{i+1}/{len(df)} → {url} → {result}")

    time.sleep(2)

# =========================================================
# SAVE OUTPUT
# =========================================================
df["employer_inferred"] = employers
df["tenure"] = tenures
df["confidence"] = confidences

df.to_csv("../output/final_dataset.csv", index=False)

print("\nDONE → final_dataset.csv created successfully")