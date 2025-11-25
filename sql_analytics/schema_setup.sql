-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS job_trends;
USE job_trends;

-- 2. Create the Master Table (Unified Schema)
CREATE TABLE IF NOT EXISTS master_job_list (
    master_id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    skills TEXT,
    posted_date DATE,
    date_scraped DATE,
    original_source VARCHAR(100)
);

-- 3. Data Cleaning & Consolidation Logic
-- (This explains how we merged Live Data + Kaggle Data)
-- INSERT INTO master_job_list (...) SELECT ... FROM job_postings;
-- INSERT INTO master_job_list (...) SELECT ... FROM kaggle_jobs;