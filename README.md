#  Job Market Analysis

## Project Overview

India Job Market Analysis is a Python-based data analytics project that explores job postings across Indian cities. It uses an interactive Streamlit dashboard to help users examine job opportunities, salary ranges, job titles, seniority levels, work arrangements, and in-demand skills.

## Features

- Interactive job market dashboard
- Job postings by city and state
- Job title and seniority analysis
- Salary analysis in Indian Rupees (INR)
- Remote and other work arrangement analysis
- In-demand skills analysis
- Filters for exploring job postings
- Filtered data export, where supported by the dashboard

## Technologies Used

- Python
- Pandas
- Streamlit
- Data visualization

## Project Structure

```text
Job_Market_Analysis/
├── app.py
├── analysis.py
├── data_quality.py
├── data/
├── requirements.txt
└── README.md
```

## How to Run the Project

1. Install Python.
2. Open a terminal in the project directory.
3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

5. Open the local URL displayed in the terminal.

## Dataset Disclaimer

If the included dataset contains synthetic or sample records, those records are for demonstration and analysis practice only. They should not be interpreted as verified, current job vacancies or actual market statistics.

## Project Goal

The goal of this project is to practice data analysis, data visualization, and presenting job market information through an interactive dashboard.