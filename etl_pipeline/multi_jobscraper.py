import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime, timedelta
import re

# ================================
# 1. MYSQL CONNECTION
# ================================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8106",   # <--- change to your password
    database="job_trends"
)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    job_id VARCHAR(255),
    title TEXT,
    company VARCHAR(255),
    location VARCHAR(255),
    skills TEXT,
    posted_date DATE,
    scraped_at DATETIME
)
""")
db.commit()

# Helper to parse dates
def parse_date(text):
    """
    Converts things like:
    'Posted 3 days ago'
    '2 weeks ago'
    '2025-01-19'
    into actual Python date.
    """
    text = text.lower()

    # Direct date
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except:
        pass

    # Days ago
    if "day" in text:
        num = int(re.findall(r"\d+", text)[0])
        return (datetime.today() - timedelta(days=num)).date()

    # Weeks ago
    if "week" in text:
        num = int(re.findall(r"\d+", text)[0])
        return (datetime.today() - timedelta(days=num * 7)).date()

    # fallback → today
    return datetime.today().date()


# Date filter
LAST_30_DAYS = datetime.today().date() - timedelta(days=30)


# ================================
# 2. SCRAPER — REMOTEOK
# ================================
def scrape_remoteok():
    print("\n🔵 Scraping RemoteOK...")
    url = "https://remoteok.com/api"

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
    except:
        print("⚠ RemoteOK failed")
        return []

    jobs = []
    for j in data[1:]:  # skip metadata row
        date_str = j.get("date", "").split("T")[0]
        posted = parse_date(date_str)

        if posted < LAST_30_DAYS:
            continue

        jobs.append({
            "platform": "RemoteOK",
            "job_id": str(j.get("id", "")),
            "title": j.get("position", "No title"),
            "company": j.get("company", "Unknown"),
            "location": j.get("location", "Remote"),
            "skills": ", ".join(j.get("tags", [])),
            "posted_date": posted
        })

    print(f"✔ RemoteOK: {len(jobs)} jobs in last 30 days")
    return jobs


# ================================
# 3. SCRAPER — WWR
# ================================
def scrape_weworkremotely():
    print("\n🟠 Scraping WeWorkRemotely...")
    url = "https://weworkremotely.com/remote-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        print("⚠ WWR failed")
        return []

    sections = soup.select("section.jobs")
    jobs = []

    for sec in sections:
        for li in sec.select("li.feature"):
            job_link = li.find("a", href=True)

            if not job_link:
                continue

            title = li.find("span", class_="title")
            company = li.find("span", class_="company")
            date_tag = li.find("time")

            posted = parse_date(date_tag["datetime"]) if date_tag else datetime.today().date()

            if posted < LAST_30_DAYS:
                continue

            jobs.append({
                "platform": "WeWorkRemotely",
                "job_id": job_link["href"],
                "title": title.text.strip() if title else "No title",
                "company": company.text.strip() if company else "Unknown",
                "location": "Remote",
                "skills": "",
                "posted_date": posted
            })

    print(f"✔ WWR: {len(jobs)} jobs in last 30 days")
    return jobs


# ================================
# 4. SCRAPER — HIMALAYAS
# ================================
def scrape_himalayas():
    print("\n🟣 Scraping Himalayas...")
    url = "https://himalayas.app/jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        print("⚠ Himalayas failed")
        return []

    cards = soup.select("a.group")
    jobs = []

    for card in cards:
        title = card.select_one(".font-semibold")
        company = card.select_one(".text-gray-500")
        tags = card.select(".inline-flex")

        posted = datetime.today().date()   # they don’t show dates → assume current

        if posted < LAST_30_DAYS:
            continue

        jobs.append({
            "platform": "Himalayas",
            "job_id": card.get("href", "unknown"),
            "title": title.text.strip() if title else "No title",
            "company": company.text.strip() if company else "Unknown",
            "location": "Remote",
            "skills": ", ".join([t.text.strip() for t in tags]),
            "posted_date": posted
        })

    print(f"✔ Himalayas: {len(jobs)} jobs (recent only)")
    return jobs


# ================================
# SAVE TO MYSQL
# ================================
def save_job(job):
    sql = """
    INSERT INTO jobs (platform, job_id, title, company, location, skills, posted_date, scraped_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        job["platform"],
        job["job_id"],
        job["title"],
        job["company"],
        job["location"],
        job["skills"],
        job["posted_date"],
        datetime.now()
    ))

    db.commit()


# ================================
# MAIN
# ================================
def main():
    print("\n==============================")
    print("🚀 Job Market Scraper (Last 30 Days)")
    print("==============================\n")

    all_jobs = []
    all_jobs += scrape_remoteok()
    all_jobs += scrape_weworkremotely()
    all_jobs += scrape_himalayas()

    print(f"\n📌 Total Jobs (last 30 days): {len(all_jobs)}")

    for job in all_jobs:
        save_job(job)

    print("\n✅ Saved to MySQL successfully!")


main()
