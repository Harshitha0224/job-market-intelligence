/* =============================================================================
   JOB MARKET TREND ANALYSIS - KEY PERFORMANCE INDICATORS (KPIs)
=============================================================================
   Purpose: To derive actionable insights regarding market velocity, 
   concentration, and skill demand from the master_job_list table.
*/

-- KPI 1: Market Velocity (Month-Over-Month Growth Rate)
-- Logic: Uses LAG() window function to compare current vs previous month volume.
WITH MonthlyStats AS (
    SELECT 
        DATE_FORMAT(posted_date, '%Y-%m') AS job_month,
        COUNT(*) AS total_jobs
    FROM master_job_list
    WHERE posted_date IS NOT NULL
    GROUP BY job_month
)
SELECT 
    job_month, 
    total_jobs,
    LAG(total_jobs) OVER (ORDER BY job_month) AS previous_month,
    ROUND(
        (total_jobs - LAG(total_jobs) OVER (ORDER BY job_month)) / 
        LAG(total_jobs) OVER (ORDER BY job_month) * 100
    , 2) AS growth_rate_pct
FROM MonthlyStats;

-- KPI 2: Market Concentration (Pareto Analysis / 80-20 Rule)
-- Logic: Identifies if the market is dominated by a few players or fragmented.
WITH CompanyCounts AS (
    SELECT company, COUNT(*) as job_count
    FROM master_job_list
    GROUP BY company
)
SELECT 
    company, 
    job_count,
    SUM(job_count) OVER (ORDER BY job_count DESC) as running_total,
    SUM(job_count) OVER () as total_market_jobs,
    ROUND((SUM(job_count) OVER (ORDER BY job_count DESC) / SUM(job_count) OVER ()) * 100, 2) as cumulative_market_share
FROM CompanyCounts
LIMIT 10;

-- KPI 3: Skill Co-Occurrence Matrix (The "Full Stack" Demand)
-- Logic: Calculates the probability of complementary skills appearing together.
SELECT 
    'Python' as primary_skill,
    SUM(CASE WHEN skills LIKE '%SQL%' THEN 1 ELSE 0 END) as paired_with_sql,
    SUM(CASE WHEN skills LIKE '%AWS%' THEN 1 ELSE 0 END) as paired_with_aws,
    SUM(CASE WHEN skills LIKE '%Tableau%' THEN 1 ELSE 0 END) as paired_with_tableau,
    COUNT(*) as total_python_jobs
FROM master_job_list
WHERE skills LIKE '%Python%';

-- KPI 4: Platform "Freshness" Index
-- Logic: Determines the latency between job posting and data ingestion.
SELECT 
    platform,
    COUNT(*) as total_jobs,
    ROUND(AVG(DATEDIFF(date_scraped, posted_date)), 1) as avg_job_age_days,
    SUM(CASE WHEN DATEDIFF(date_scraped, posted_date) > 30 THEN 1 ELSE 0 END) as stale_jobs_count
FROM master_job_list
GROUP BY platform
ORDER BY avg_job_age_days ASC;

-- KPI 5: High-Value "Unicorn" Opportunity Search
-- Logic: Filters for specific high-demand criteria (Python + Data Skills).
SELECT 
    title, 
    company, 
    posted_date, 
    platform
FROM master_job_list
WHERE 
    (skills LIKE '%Python%' OR skills LIKE '%Data%') 
ORDER BY posted_date DESC
LIMIT 10;