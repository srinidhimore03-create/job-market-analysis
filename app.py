from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Job Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "india_job_postings_30_cities_sample.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    required_columns = [
        "title",
        "city",
        "country",
        "seniority",
        "remote",
        "salary_min_inr",
        "salary_max_inr",
        "skills"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns: " + ", ".join(missing_columns)
        )

    # Clean text columns
    text_columns = [
        "title", "city", "country", "seniority",
        "remote", "skills", "company", "state",
        "posting_id", "posted_on", "employment_type"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # Convert salary columns to numbers
    for column in ["salary_min_inr", "salary_max_inr"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Keep Indian records only
    country = (
        df["country"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    india_df = df[
        country.isin([
            "india",
            "in",
            "ind",
            "republic of india"
        ])
    ].copy()

    # Salary values are already in INR
    india_df["salary_mid_inr"] = (
        india_df["salary_min_inr"]
        + india_df["salary_max_inr"]
    ) / 2

    # Convert annual INR salary to LPA
    india_df["salary_min_lpa"] = (
        india_df["salary_min_inr"] / 100000
    )

    india_df["salary_max_lpa"] = (
        india_df["salary_max_inr"] / 100000
    )

    india_df["salary_mid_lpa"] = (
        india_df["salary_mid_inr"] / 100000
    )

    return df, india_df


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_options(df, column):

    if column not in df.columns:
        return []

    values = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    return sorted(
        values[values != ""].unique().tolist()
    )


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🇮🇳 Job Market Analysis Dashboard")

st.write(
    "Explore job opportunities, salaries, required skills, "
    "experience levels, and work arrangements across Indian cities."
)

try:
    all_jobs, india_jobs = load_data(str(DATA_FILE))

except FileNotFoundError:
    st.error(f"Dataset not found: {DATA_FILE}")

    st.info(
        "Place india_job_postings_30_cities_sample.csv "
        "inside the data folder of your project."
    )

    st.stop()

except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()


st.info(
    "Dataset notice: These are synthetic sample records for "
    "project demonstration, not verified live job vacancies. "
    "Salary figures are sample annual INR amounts."
)

st.caption(
    f"Total CSV records: {len(all_jobs):,} | "
    f"Indian records: {len(india_jobs):,} | "
    f"Cities: {india_jobs['city'].nunique():,}"
)

if india_jobs.empty:
    st.warning("No Indian records found in the CSV.")
    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🔎 Dashboard Filters")

selected_cities = st.sidebar.multiselect(
    "Indian Cities",
    options=get_options(india_jobs, "city")
)

selected_states = st.sidebar.multiselect(
    "Indian States / UTs",
    options=get_options(india_jobs, "state")
)

selected_titles = st.sidebar.multiselect(
    "Job Titles",
    options=get_options(india_jobs, "title")
)

selected_seniority = st.sidebar.multiselect(
    "Seniority Levels",
    options=get_options(india_jobs, "seniority")
)

selected_remote = st.sidebar.multiselect(
    "Work Arrangements",
    options=get_options(india_jobs, "remote")
)

if st.sidebar.button(
    "Reset Filters",
    use_container_width=True
):
    st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = india_jobs.copy()

if selected_cities:
    filtered_df = filtered_df[
        filtered_df["city"].isin(selected_cities)
    ]

if selected_states and "state" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["state"].isin(selected_states)
    ]

if selected_titles:
    filtered_df = filtered_df[
        filtered_df["title"].isin(selected_titles)
    ]

if selected_seniority:
    filtered_df = filtered_df[
        filtered_df["seniority"].isin(selected_seniority)
    ]

if selected_remote:
    filtered_df = filtered_df[
        filtered_df["remote"].isin(selected_remote)
    ]

if filtered_df.empty:
    st.warning(
        "No records match your filters. "
        "Please change your selections or reset the filters."
    )
    st.stop()


# ============================================================
# KEY STATISTICS
# ============================================================

st.divider()
st.header("📌 Key Statistics")

salary_df = filtered_df.dropna(
    subset=["salary_min_inr", "salary_max_inr"]
)

average_salary = (
    salary_df["salary_mid_lpa"].mean()
    if not salary_df.empty
    else None
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Sample Listings",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Average Sample Salary",
    f"₹{average_salary:.2f} LPA"
    if pd.notna(average_salary)
    else "N/A"
)

col3.metric(
    "Unique Job Titles",
    f"{filtered_df['title'].nunique():,}"
)

col4.metric(
    "Listings With Salary",
    f"{len(salary_df):,}"
)

st.caption(
    "LPA means lakhs per annum. These figures describe "
    "the sample dataset, not verified market salaries."
)


# ============================================================
# JOB TITLE ANALYSIS
# ============================================================

st.divider()
st.header("💼 Job Title Analysis")

jobs_by_title = (
    filtered_df["title"]
    .replace("", pd.NA)
    .dropna()
    .value_counts()
    .head(10)
    .sort_values()
)

if not jobs_by_title.empty:

    st.bar_chart(
        jobs_by_title,
        horizontal=True,
        x_label="Sample Job Listings",
        y_label="Job Title",
        use_container_width=True
    )

else:
    st.info("No job title information available.")


# ============================================================
# SENIORITY ANALYSIS
# ============================================================

st.divider()
st.header("🎯 Seniority Level Analysis")

col1, col2 = st.columns(2)

with col1:

    seniority_counts = (
        filtered_df["seniority"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    if not seniority_counts.empty:

        st.bar_chart(
            seniority_counts,
            x_label="Seniority Level",
            y_label="Sample Job Listings",
            use_container_width=True
        )

with col2:

    st.subheader("Seniority Summary")

    seniority_table = (
        filtered_df["seniority"]
        .replace("", pd.NA)
        .fillna("Not specified")
        .value_counts()
        .rename_axis("Seniority Level")
        .reset_index(name="Sample Listings")
    )

    st.dataframe(
        seniority_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SALARY ANALYSIS
# ============================================================

st.divider()
st.header("💰 Salary Analysis")

if not salary_df.empty:

    salary_summary = (
        salary_df.groupby("title")
        .agg(
            Sample_Listings=("title", "size"),
            Average_Min_LPA=("salary_min_lpa", "mean"),
            Average_Max_LPA=("salary_max_lpa", "mean"),
            Average_Mid_LPA=("salary_mid_lpa", "mean")
        )
        .sort_values(
            "Sample_Listings",
            ascending=False
        )
        .head(10)
    )

    st.subheader("Sample Salary Ranges by Job Title")

    salary_chart = salary_summary[
        ["Average_Min_LPA", "Average_Max_LPA"]
    ].rename(
        columns={
            "Average_Min_LPA": "Minimum Salary (LPA)",
            "Average_Max_LPA": "Maximum Salary (LPA)"
        }
    )

    st.bar_chart(
        salary_chart,
        x_label="Job Title",
        y_label="Salary (LPA)",
        use_container_width=True
    )

    display_salary = (
        salary_summary
        .reset_index()
        .rename(
            columns={
                "title": "Job Title",
                "Sample_Listings": "Sample Listings",
                "Average_Min_LPA": "Average Minimum (LPA)",
                "Average_Max_LPA": "Average Maximum (LPA)",
                "Average_Mid_LPA": "Average Midpoint (LPA)"
            }
        )
    )

    st.subheader("Salary Summary Table")

    st.dataframe(
        display_salary.round(2),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No salary information available.")


# ============================================================
# CITY ANALYSIS
# ============================================================

st.divider()
st.header("📍 Indian City Analysis")

city_counts = (
    filtered_df["city"]
    .replace("", pd.NA)
    .dropna()
    .value_counts()
)

if not city_counts.empty:

    st.subheader("Top Cities by Sample Listings")

    st.bar_chart(
        city_counts.head(10).sort_values(),
        horizontal=True,
        x_label="Sample Job Listings",
        y_label="City",
        use_container_width=True
    )

    city_summary = (
        filtered_df.groupby("city")
        .agg(
            Sample_Listings=("title", "size"),
            Unique_Job_Titles=("title", "nunique")
        )
        .sort_values(
            "Sample_Listings",
            ascending=False
        )
        .reset_index()
        .rename(
            columns={
                "city": "City",
                "Sample_Listings": "Sample Listings",
                "Unique_Job_Titles": "Unique Job Titles"
            }
        )
    )

    st.subheader("City Summary")

    st.dataframe(
        city_summary,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No city information available.")


# ============================================================
# WORK ARRANGEMENT ANALYSIS
# ============================================================

st.divider()
st.header("🏢 Work Arrangement Analysis")

work_counts = (
    filtered_df["remote"]
    .replace("", pd.NA)
    .dropna()
    .value_counts()
)

if not work_counts.empty:

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            work_counts,
            x_label="Work Arrangement",
            y_label="Sample Listings",
            use_container_width=True
        )

    with col2:

        st.dataframe(
            work_counts
            .rename_axis("Work Arrangement")
            .reset_index(name="Sample Listings"),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SKILLS ANALYSIS
# ============================================================

st.divider()
st.header("🧠 In-Demand Skills Analysis")

# Skills in the supplied CSV are comma-separated.
skill_series = (
    filtered_df["skills"]
    .fillna("")
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
)

skill_series = skill_series[skill_series != ""]

if not skill_series.empty:

    skill_counts = skill_series.value_counts()

    st.subheader("Top 15 Skills")

    st.bar_chart(
        skill_counts.head(15).sort_values(),
        horizontal=True,
        x_label="Sample Skill Mentions",
        y_label="Skill",
        use_container_width=True
    )

    st.subheader("Skills Frequency Table")

    st.dataframe(
        skill_counts.head(15)
        .rename_axis("Skill")
        .reset_index(name="Mentions"),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("💡 Skills Recommendations")

    st.write(
        "Skills mentioned most often in the selected sample records:"
    )

    for rank, (skill, count) in enumerate(
        skill_counts.head(5).items(),
        start=1
    ):

        st.write(
            f"**{rank}. {skill}** — mentioned {count} times"
        )

    st.caption(
        "Recommendations reflect this sample dataset only "
        "and do not guarantee employment."
    )

else:
    st.info("No skills information available.")


# ============================================================
# FILTERED JOB LISTINGS
# ============================================================

st.divider()
st.header("📋 Filtered Indian Job Listings")

display_columns = [
    "posting_id",
    "posted_on",
    "title",
    "company",
    "seniority",
    "city",
    "state",
    "country",
    "remote",
    "salary_min_inr",
    "salary_max_inr",
    "skills",
    "employment_type"
]

display_columns = [
    column for column in display_columns
    if column in filtered_df.columns
]

display_df = filtered_df[display_columns].copy()

display_df = display_df.rename(
    columns={
        "posting_id": "Sample Posting ID",
        "posted_on": "Sample Posted On",
        "title": "Job Title",
        "company": "Sample Company Name",
        "seniority": "Seniority",
        "city": "City",
        "state": "State / UT",
        "country": "Country",
        "remote": "Work Arrangement",
        "salary_min_inr": "Minimum Annual Salary (INR)",
        "salary_max_inr": "Maximum Annual Salary (INR)",
        "skills": "Required Skills",
        "employment_type": "Employment Type"
    }
)

if "Minimum Annual Salary (INR)" in display_df.columns:

    display_df["Minimum Salary (LPA)"] = (
        pd.to_numeric(
            filtered_df["salary_min_inr"],
            errors="coerce"
        ) / 100000
    ).round(2).values

if "Maximum Annual Salary (INR)" in display_df.columns:

    display_df["Maximum Salary (LPA)"] = (
        pd.to_numeric(
            filtered_df["salary_max_inr"],
            errors="coerce"
        ) / 100000
    ).round(2).values

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

csv_data = display_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download Filtered Sample Job Listings",
    data=csv_data,
    file_name="filtered_indian_sample_job_listings.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Job Market Analysis and Skills Recommendation System | "
    "Built with Python, Pandas, and Streamlit"
)

st.caption(
    "Data note: all records in this CSV are synthetic practice examples, "
    "not verified live job vacancies."
)