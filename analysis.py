import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

DATA_FILE = Path("data/data-job-postings.csv")
CHART_DIR = Path("charts")
OUTPUT_DIR = Path("data")

CHART_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# 2. LOAD DATA
# ==========================================

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print("=" * 50)
print("JOB MARKET ANALYSIS")
print("=" * 50)

print(f"\nTotal job postings: {len(df):,}")
print(f"Total columns: {len(df.columns)}")


# ==========================================
# 3. PREPARE DATA
# ==========================================

df["salary_min_usd"] = pd.to_numeric(
    df["salary_min_usd"],
    errors="coerce"
)

df["salary_max_usd"] = pd.to_numeric(
    df["salary_max_usd"],
    errors="coerce"
)

df["salary_mid_usd"] = (
    df["salary_min_usd"] + df["salary_max_usd"]
) / 2

df["skill_list"] = df["skills"].fillna("").apply(
    lambda value: [
        skill.strip().lower()
        for skill in value.split("|")
        if skill.strip()
    ]
)


# ==========================================
# 4. JOB TITLE ANALYSIS
# ==========================================

print("\n--- TOP 10 JOB TITLES ---")

job_counts = df["title"].value_counts()

print(job_counts.head(10))

job_counts.rename_axis("Job_Title").reset_index(
    name="Job_Count"
).to_csv(
    OUTPUT_DIR / "jobs_by_title.csv",
    index=False
)

fig, ax = plt.subplots(figsize=(10, 6))

job_counts.head(10).sort_values().plot(
    kind="barh",
    ax=ax
)

ax.set_title("Top 10 Job Titles")
ax.set_xlabel("Number of Job Postings")
ax.set_ylabel("Job Title")

fig.tight_layout()
fig.savefig(CHART_DIR / "jobs_by_title.png", dpi=150)
plt.close(fig)


# ==========================================
# 5. SALARY ANALYSIS
# ==========================================

salary_df = df.dropna(
    subset=["salary_min_usd", "salary_max_usd"]
).copy()

salary_df = salary_df[
    (salary_df["salary_min_usd"] > 0)
    & (salary_df["salary_max_usd"] >= salary_df["salary_min_usd"])
]

salary_df["salary_mid_usd"] = (
    salary_df["salary_min_usd"]
    + salary_df["salary_max_usd"]
) / 2

salary_summary = (
    salary_df.groupby("title")
    .agg(
        Job_Count=("posting_id", "count"),
        Average_Min_Salary=("salary_min_usd", "mean"),
        Average_Max_Salary=("salary_max_usd", "mean"),
        Average_Salary_Midpoint=("salary_mid_usd", "mean")
    )
    .sort_values("Average_Salary_Midpoint", ascending=False)
)

salary_summary.round(2).to_csv(
    OUTPUT_DIR / "salary_analysis.csv"
)

print("\n--- TOP 10 JOB TITLES BY AVERAGE SALARY MIDPOINT ---")
print(salary_summary.head(10).round(2))

top_salary = salary_summary[
    "Average_Salary_Midpoint"
].sort_values().tail(10)

if not top_salary.empty:
    fig, ax = plt.subplots(figsize=(10, 6))

    top_salary.plot(
        kind="barh",
        ax=ax
    )

    ax.set_title("Top 10 Job Titles by Average Salary Midpoint")
    ax.set_xlabel("Average Salary Midpoint (USD)")
    ax.set_ylabel("Job Title")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "average_salary.png", dpi=150)
    plt.close(fig)


# ==========================================
# 6. SKILLS ANALYSIS
# ==========================================

all_skills = df["skill_list"].explode().dropna()

skill_counts = all_skills.value_counts()

skill_summary = pd.DataFrame({
    "Skill": skill_counts.index,
    "Skill_Mentions": skill_counts.values
})

skill_summary.to_csv(
    OUTPUT_DIR / "skill_analysis.csv",
    index=False
)

print("\n--- TOP 15 SKILLS ---")
print(skill_summary.head(15).to_string(index=False))

top_skills = skill_counts.head(15).sort_values()

if not top_skills.empty:
    fig, ax = plt.subplots(figsize=(10, 6))

    top_skills.plot(
        kind="barh",
        ax=ax
    )

    ax.set_title("Top 15 Frequently Mentioned Skills")
    ax.set_xlabel("Number of Skill Mentions")
    ax.set_ylabel("Skill")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "top_skills.png", dpi=150)
    plt.close(fig)


# ==========================================
# 7. LOCATION ANALYSIS
# ==========================================

city_counts = df["city"].value_counts()

city_summary = city_counts.rename_axis(
    "City"
).reset_index(
    name="Job_Count"
)

city_summary.to_csv(
    OUTPUT_DIR / "jobs_by_city.csv",
    index=False
)

print("\n--- TOP 10 CITIES BY JOB POSTINGS ---")
print(city_counts.head(10))

top_cities = city_counts.head(10).sort_values()

fig, ax = plt.subplots(figsize=(10, 6))

top_cities.plot(
    kind="barh",
    ax=ax
)

ax.set_title("Top 10 Cities by Job Postings")
ax.set_xlabel("Number of Job Postings")
ax.set_ylabel("City")

fig.tight_layout()
fig.savefig(CHART_DIR / "jobs_by_location.png", dpi=150)
plt.close(fig)


# ==========================================
# 8. WORK ARRANGEMENT ANALYSIS
# ==========================================

work_counts = df["remote"].value_counts()

work_summary = pd.DataFrame({
    "Work_Arrangement": work_counts.index,
    "Job_Count": work_counts.values,
    "Percentage": (
        work_counts.values / len(df) * 100
    ).round(2)
})

work_summary.to_csv(
    OUTPUT_DIR / "work_arrangement_analysis.csv",
    index=False
)

print("\n--- WORK ARRANGEMENTS ---")
print(work_summary.to_string(index=False))


# ==========================================
# 9. DATA QUALITY SUMMARY
# ==========================================

quality_summary = pd.DataFrame({
    "Column": df.columns,
    "Missing_Values": [
        int(df[column].isna().sum())
        for column in df.columns
    ]
})

quality_summary.to_csv(
    OUTPUT_DIR / "data_quality_report.csv",
    index=False
)

print("\n--- DATA QUALITY ---")
print(quality_summary.to_string(index=False))


# ==========================================
# 10. COMPLETION
# ==========================================

print("\n" + "=" * 50)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 50)

print(f"\nCharts saved in: {CHART_DIR.resolve()}")
print(f"Analysis files saved in: {OUTPUT_DIR.resolve()}")

print("\nGenerated charts:")
print("- jobs_by_title.png")
print("- average_salary.png")
print("- top_skills.png")
print("- jobs_by_location.png")