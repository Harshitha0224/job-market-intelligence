import pandas as pd
import mysql.connector
from datetime import datetime

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8106",
    database="job_trends"
)
cursor = db.cursor()

# --- CHANGE 1: Use read_excel instead of read_csv ---
# Make sure the file name matches exactly what you have in your folder
df = pd.read_csv("kaggle_jobs.csv")

# Rename columns to match MySQL fields
df = df.rename(columns={
    "jobtitle": "title",
    "company": "company",
    "joblocation_address": "location",
    "skills": "skills",
    "postdate": "date_scraped"
})

# Insert rows
for _, row in df.iterrows():
    sql = """
    INSERT INTO kaggle_jobs (platform, title, company, location, skills, date_scraped, source_file)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        "Kaggle",
        str(row["title"])
        ,
        str(row["company"]),
        str(row["location"]),
        str(row["skills"]),
        # Excel often reads dates as datetime objects automatically, so this handles both
        pd.to_datetime(row["date_scraped"], errors="coerce").date() if pd.notnull(row["date_scraped"]) else None,
        "kaggle_jobs.xlsx" # --- CHANGE 2: Updated source file name for the DB record ---
    ))

db.commit()
print("✔ Kaggle data imported successfully!")