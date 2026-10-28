import pandas as pd


def check_data_quality(df):
    """
    Check the quality of the India Job Market dataset.
    Returns a dictionary containing data quality results.
    """

    report = {}

    # 1. Total records
    report["Total Records"] = len(df)

    # 2. Duplicate records
    report["Duplicate Records"] = int(df.duplicated().sum())

    # 3. Missing values
    report["Total Missing Values"] = int(df.isnull().sum().sum())

    # 4. Missing values by column
    missing_values = df.isnull().sum()
    report["Missing Values by Column"] = missing_values[
        missing_values > 0
    ].to_dict()

    # 5. Missing job titles
    if "title" in df.columns:
        report["Missing Job Titles"] = int(
            df["title"].isnull().sum()
        )

    # 6. Missing company names
    if "company" in df.columns:
        report["Missing Company Names"] = int(
            df["company"].isnull().sum()
        )

    # 7. Invalid salary records
    if {
        "salary_min_inr",
        "salary_max_inr"
    }.issubset(df.columns):

        salary_min = pd.to_numeric(
            df["salary_min_inr"], errors="coerce"
        )

        salary_max = pd.to_numeric(
            df["salary_max_inr"], errors="coerce"
        )

        invalid_salary = (
            (salary_min < 0)
            | (salary_max < 0)
            | (salary_min > salary_max)
        )

        report["Invalid Salary Records"] = int(
            invalid_salary.fillna(False).sum()
        )

    # 8. Missing city names
    if "city" in df.columns:
        report["Missing City Names"] = int(
            df["city"].isnull().sum()
        )

    # 9. Missing state names
    if "state" in df.columns:
        report["Missing State Names"] = int(
            df["state"].isnull().sum()
        )

    return report