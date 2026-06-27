import pandas as pd
import os

# ==========================
# Read GitHub profile data
# ==========================

profiles_file = "../output/profiles.csv"

if not os.path.exists(profiles_file):
    raise FileNotFoundError(
        "❌ profiles.csv not found. Run profile.py first."
    )

df = pd.read_csv(profiles_file)

# ==========================
# Target company
# ==========================

# OpenAI Codex
TARGET_COMPANY = "openai"

# Uncomment for Gemini CLI
# TARGET_COMPANY = "google"

# ==========================
# Classification Function
# ==========================

def classify(login, company, bio):

    login = str(login).lower() if pd.notna(login) else ""
    company = str(company).lower() if pd.notna(company) else ""
    bio = str(bio).lower() if pd.notna(bio) else ""

    # Strongest signal
    if TARGET_COMPANY in company:
        return "Internal", "High"

    # Medium confidence
    if TARGET_COMPANY in bio:
        return "Internal", "Medium"

    # Username heuristic
    if TARGET_COMPANY in login:
        return "Internal", "Medium"

    # Common OpenAI naming convention
    if TARGET_COMPANY == "openai" and login.endswith("-oai"):
        return "Internal", "Medium"

    return "External", "Low"

# ==========================
# Apply classification
# ==========================

classification = df.apply(
    lambda row: classify(
        row["github_login"],
        row["company"],
        row["bio"]
    ),
    axis=1
)

df["internal_or_external"] = [c[0] for c in classification]
df["classification_confidence"] = [c[1] for c in classification]

# ==========================
# Save output
# ==========================

output_file = "../output/classified_contributors.csv"
df.to_csv(output_file, index=False)

# ==========================
# Print summary
# ==========================

print("\n✅ Classification Complete!\n")

print(df[
    [
        "github_login",
        "company",
        "bio",
        "internal_or_external",
        "classification_confidence"
    ]
].head(10))

print("\nSummary")
print("---------------------------")
print(df["internal_or_external"].value_counts())

internal = (df["internal_or_external"] == "Internal").sum()
external = (df["internal_or_external"] == "External").sum()

print(f"\nInternal Contributors : {internal}")
print(f"External Contributors : {external}")

print(f"\nSaved to: {output_file}")