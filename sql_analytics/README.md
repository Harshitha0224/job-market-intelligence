# 🧠 SQL Analytics & KPIs

This directory contains the SQL scripts used to transform raw job data into actionable market intelligence.

## 📂 File Overview

| File | Description |
| :--- | :--- |
| `schema_setup.sql` | DDL commands to create the database schema and consolidate raw tables. |
| `advanced_kpis.sql` | The core analytical queries used to generate the project's insights. |

## 📊 Analytical Techniques Used

### 1. Window Functions (`LAG`, `SUM OVER`)
Used to calculate **Month-Over-Month Growth** and **Cumulative Market Share**. This allows us to see trends over time and understand market fragmentation without using external tools like Excel.

### 2. Common Table Expressions (CTEs)
Used to structure complex queries, such as the **Pareto Analysis**, making the code readable and modular.

### 3. Case Statements & Aggregations
Used to build the **Skill Co-Occurrence Matrix**, effectively pivoting row-level string data into columnar insights (e.g., counting how often "AWS" appears in "Python" jobs).

### 4. Date Math (`DATEDIFF`, `DATE_SUB`)
Used to calculate the **Freshness Index** of different job platforms and to filter for "Unicorn" opportunities within specific time windows.