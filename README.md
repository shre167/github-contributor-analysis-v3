# GitHub Contributor Analysis + LinkedIn Enrichment Pipeline

A data engineering pipeline that analyzes GitHub repositories to classify internal vs. external contributions, then enriches top contributor profiles with LinkedIn data to infer employer, career history, and estimated tenure.
Final Dataset: https://drive.google.com/file/d/1mW9fsbxK9obS98_ltzHeAyRHNH0HG89J/view?usp=sharing

---

## Task Context

This project was built as part of the **Huntd Interview Take-Home Round (Task 1)**. The objective was to:

1. Analyze two AI CLI repositories — [OpenAI Codex CLI](https://github.com/openai/codex) and [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) — and estimate the split between **internal (employee) vs. external (community) contributions**.
2. Enrich the **top contributors** with professional data sourced from LinkedIn — current employer, inferred tenure, and confidence scores.

The pipeline is built to be **repo-agnostic**: point it at any GitHub repository, and it will produce the same structured output.

---

## Problem Statement

GitHub contribution data is purely technical — it tells you who committed code, but nothing about who those people are professionally. This pipeline bridges that gap by resolving GitHub contributors to their LinkedIn profiles and enriching each record with employer and tenure data, enabling analysis of the professional composition of any open-source project.

---

## Repositories Analyzed

| Repository | Company | URL |
|---|---|---|
| Codex CLI | OpenAI | [github.com/openai/codex](https://github.com/openai/codex) |
| Gemini CLI | Google | [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |

---

## System Pipeline / Workflow

```
GitHub Repository URL
        │
        ▼
1. Extract Contributors         [github_analysis.py]
   └── Pull contributor list + commit counts via GitHub API
   └── Classify as internal / external based on org membership & email domain

        │
        ▼
2. Search LinkedIn Profiles     [linkedin_search.py]
   └── Use Apify Google Search actor to find LinkedIn URLs
   └── Match GitHub names/usernames to LinkedIn profiles

        │
        ▼
3. Scrape LinkedIn Profiles     [linkedin_enrichment.py]
   └── Fetch structured profile data via Bright Data LinkedIn Scraper API
   └── Extract current role, employer, and employment history

        │
        ▼
4. Classify & Infer             [classify.py]
   └── Bucket employers: OpenAI / Google / Anthropic / xAI / Other
   └── Calculate tenure from start date to present
   └── Assign confidence scores (high / medium / low)

        │
        ▼
5. Consolidate Output           [contribution_analysis.py]
   └── Merge all fields into final enriched dataset
   └── Generate contribution_summary and report.md
```

---

## Output Dataset Schema

The final dataset (`output/final_dataset.csv`) contains the following fields as specified by the task:

| Field | Description |
|---|---|
| `repo` | Repository name (e.g. `openai/codex`) |
| `github_login` | GitHub username of the contributor |
| `github_id` | Numeric GitHub user ID |
| `name` | Full name (from GitHub or LinkedIn) |
| `contribution_metric` | Commit count used as the contribution signal |
| `internal_or_external` | `Internal` if affiliated with the repo's parent company; `External` otherwise |
| `employer_inferred` | Current employer extracted from LinkedIn Experience section |
| `employer_confidence` | Match confidence: `high` / `medium` / `low` |
| `linkedin_url` | Resolved LinkedIn profile URL |
| `tenure_current_employer_years` | Estimated years at current employer (calculated from start date) |
| `tenure_confidence` | Confidence in tenure estimate: `high` / `medium` / `low` |

Incomplete or unresolvable records are marked `Unknown` with `low` confidence — not omitted.

---

## Tools & Technologies Used

| Category | Tool / Service |
|---|---|
| Language | Python 3 |
| GitHub Data | GitHub REST API via `PyGitHub` |
| LinkedIn Discovery | Apify — Google Search Actor |
| LinkedIn Scraping | Bright Data LinkedIn Scraper API |
| Data Processing | `pandas` |
| Environment Config | `.env` via `python-dotenv` |
| Output Format | CSV + Markdown report |

---

## Required API Keys

Add the following to a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_personal_access_token
BRIGHTDATA_API_KEY=your_brightdata_api_key
APIFY_API_TOKEN=your_apify_api_token
```

| Key | Where to get it |
|---|---|
| `GITHUB_TOKEN` | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `BRIGHTDATA_API_KEY` | [brightdata.com](https://brightdata.com) — LinkedIn Scraper product |
| `APIFY_API_TOKEN` | [apify.com](https://apify.com) — free tier available |

---

## Output Files

All outputs are written to the `/output/` directory:

| File | Description |
|---|---|
| `final_dataset.csv` | ✅ **Primary output** — fully enriched contributor records with all required fields |
| `dataset.csv` | Raw merged dataset before classification |
| `classified_contributors.csv` | Contributor records with employer and confidence classifications |
| `codex_contributors.csv` | Contributor subset filtered for the Codex CLI repo |
| `contribution_summary.csv` | Aggregated contribution statistics per contributor |
| `linkedin_results.csv` | Raw scrape results from Bright Data |
| `profiles.csv` | Intermediate LinkedIn profile data |

---

## Key Insights / Results

- Analyzed contributors across both repositories and classified each as internal (employee) or external (community contributor) using commit-based signals and org membership
- Enriched top contributors with LinkedIn-sourced professional data including current employer and tenure
- Employer bucketing focuses on: **OpenAI, Google, Anthropic, xAI** — with all others labeled by actual employer name
- Produced a structured, analysis-ready CSV joining GitHub activity with professional background data

> Match rates and coverage vary based on GitHub profile completeness and LinkedIn data availability.

---

## How to Run

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd github-contributor-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys

# 4. Run the full pipeline
python analysis-code/github_analysis.py
python analysis-code/linkedin_search.py
python analysis-code/linkedin_enrichment.py
python analysis-code/classify.py
python analysis-code/contribution_analysis.py
```

Final enriched dataset: `output/final_dataset.csv`  
Analysis report: `report.md`

---

## Limitations

- **LinkedIn coverage gaps** — Not all GitHub contributors have public or discoverable LinkedIn profiles
- **Scraping constraints** — Subject to Bright Data API rate limits and LinkedIn's anti-scraping measures
- **Tenure inference accuracy** — Relies on user-entered dates on LinkedIn; missing or overlapping date ranges reduce reliability
- **Name matching ambiguity** — GitHub usernames don't always map cleanly to real names; false positive matches are possible
- **Data freshness** — Scraped data is a point-in-time snapshot and may not reflect current employment

---

## Future Improvements

- **Visualization dashboard** — Plotly or Streamlit dashboard showing employer distribution and tenure histograms per repo
- **Improved name resolution** — NLP or fuzzy matching to reduce false positives in the GitHub-to-LinkedIn mapping step
- **ML-based confidence scoring** — Train a classifier using profile similarity signals to score match quality
- **Async scraping at scale** — Add pagination and concurrent scraping to handle repos with thousands of contributors
- **Cross-platform enrichment** — Extend enrichment to Twitter/X, personal sites, or Google Scholar for academic contributors

---

## Project Structure

```
github-contributor-analysis/
├── analysis-code/
│   ├── github_analysis.py        # GitHub API extraction + internal/external classification
│   ├── linkedin_search.py        # LinkedIn URL discovery via Apify
│   ├── linkedin_enrichment.py    # Profile scraping via Bright Data
│   ├── classify.py               # Employer bucketing + tenure inference
│   └── contribution_analysis.py  # Final merge + report generation
├── output/
│   ├── final_dataset.csv         # ✅ Primary output
│   ├── dataset.csv
│   ├── classified_contributors.csv
│   ├── codex_contributors.csv
│   ├── contribution_summary.csv
│   ├── linkedin_results.csv
│   └── profiles.csv
├── report.md                     # Contributor breakdown + findings
├── .env.example
├── requirements.txt
└── README.md
```
