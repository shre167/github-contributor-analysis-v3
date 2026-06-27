import pandas as pd
import os

# ==========================
# Files
# ==========================

classified_file = "../output/classified_contributors.csv"
contributors_file = "../output/codex_contributors.csv"

if not os.path.exists(classified_file):
    raise FileNotFoundError("classified_contributors.csv not found.")

if not os.path.exists(contributors_file):
    raise FileNotFoundError("codex_contributors.csv not found.")

classified = pd.read_csv(classified_file)
contributors = pd.read_csv(contributors_file)

# Merge to get contribution counts
df = classified.merge(
    contributors[["login", "contributions"]],
    left_on="github_login",
    right_on="login",
    how="left"
)

df.drop(columns=["login"], inplace=True)

# Fill missing contributions with 0
df["contributions"] = df["contributions"].fillna(0)

# ==========================
# Statistics
# ==========================

total_contributors = len(df)

internal_df = df[df["internal_or_external"] == "Internal"]
external_df = df[df["internal_or_external"] == "External"]

internal_count = len(internal_df)
external_count = len(external_df)

total_commits = df["contributions"].sum()

internal_commits = internal_df["contributions"].sum()
external_commits = external_df["contributions"].sum()

internal_share = (
    internal_commits / total_commits * 100
    if total_commits else 0
)

external_share = (
    external_commits / total_commits * 100
    if total_commits else 0
)

# ==========================
# Print Report
# ==========================

print("\n========== CONTRIBUTION REPORT ==========\n")

print(f"Total Contributors : {total_contributors}")
print(f"Internal Contributors : {internal_count}")
print(f"External Contributors : {external_count}")

print()

print(f"Total Contributions : {total_commits}")
print(f"Internal Contributions : {internal_commits}")
print(f"External Contributions : {external_commits}")

print()

print(f"Internal Contribution Share : {internal_share:.2f}%")
print(f"External Contribution Share : {external_share:.2f}%")

# ==========================
# Save Summary
# ==========================

summary = pd.DataFrame([{
    "total_contributors": total_contributors,
    "internal_contributors": internal_count,
    "external_contributors": external_count,
    "total_contributions": total_commits,
    "internal_contributions": internal_commits,
    "external_contributions": external_commits,
    "internal_share_percent": round(internal_share, 2),
    "external_share_percent": round(external_share, 2)
}])

summary.to_csv("../output/contribution_summary.csv", index=False)

print("\nSaved: ../output/contribution_summary.csv")