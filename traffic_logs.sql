Select* from traffic_logs
1.What are the top 10 vehicle_Number involved in drug-related stops?
Select vehicle_number,count(*)as stop_counts
from traffic_logs
where drugs_related_stop=True
group by vehicle_number
order by stop_counts DESC
limit 10;
2.Which vehicles were most frequently searched?
select vehicle_number, count(*)as search_count
from traffic_logs
where search_conducted = TRUE
group by vehicle_number
order by search_count DESC
LIMIT 10;
Demographic based
4.Which driver age group had the highest arrest rate?
select driver_age, count(*) as arrest_count
from traffic_logs
where is_arrested = TRUE
group by driver_age
order by arrest_count DESC
LIMIT 3;
5.What is the gender distribution of drivers stopped in each country?
select driver_gender,country_name,count(*) as stop_counts
from traffic_logs
group by country_name,driver_gender
order by country_name,driver_gender;
6.Which race and gender combination has the highest search rate?
select driver_race,driver_gender,count(*)as total_stops,
round(100*sum(case when search_conducted=True then 1 else 0 end)/count(*),2) as search_rate_percentage
from traffic_logs
Group by driver_race, driver_gender
order by search_rate_percentage DESC
limit 1;
🕒 Time & Duration Based
7.	What time of day sees the most traffic stops?
Select * from traffic_logs
Select
extract(hour from time_stamp) as hour_of_day,
count(*) as stop_count
From traffic_logs
group by hour_of_day
order by stop_count desc
limit 1;
Select
  case
    when extract(hour from stop_time) between 5 and 11 then 'Morning'
    when extract(hour from stop_time) between 12 and 16 then 'Afternoon'
    when extract(hour from stop_time) between 17 and 20 then 'Evening'
    else 'Night'
  end as time_of_day,
  count(*) as stop_count
from traffic_logs
group by time_of_day
order by stop_count desc;

8.	What is the average stop duration for different violations?
<15 Min	7
16-30 Min	23
30+ Min	40
Select violation,
    round(avg(
        case stop_duration
            when '<15 Min' then 7
            when '16-30 Min' then 23
            when '30+ Min' then 40
          	else null
        end
    ), 2) as avg_stop_duration_minutes
from traffic_logs
group by violation
order by avg_stop_duration_minutes desc;



9.	Are stops during the night more likely to lead to arrests?
select
    case
        when stop_time >= '20:00:00' or stop_time < '06:00:00' then 'Night'
        else 'Day'
    end as time_of_day,
    count(*) as total_stops,
    sum(case when is_arrested = TRUE then 1 else 0 end) as arrests,
    round(
        100.0 * sum(case when is_arrested = TRUE then 1 else 0 end) / count(*),
        2
    ) as arrest_rate_percentage
from traffic_logs
group by time_of_day;


⚖️ Violation-Based
10.	Which violations are most associated with searches or arrests?
select violation,count(*)as total_stops,
    sum(case when search_conducted = TRUE then 1 else 0 end) as total_searches,
    sum(case when  is_arrested = TRUE then 1 else 0 end) as  total_arrests,
    ROUND(
        100.0 * sum(case when search_conducted = TRUE then 1 else 0 end)/count(*),
        2
    ) as search_rate_percentage,
    ROUND(
        100.0 * sum(case when  is_arrested = TRUE then 1 else 0 end)/count(*),
        2
    ) as arrest_rate_percentage
from traffic_logs
group by violation
order by arrest_rate_percentage DESC, search_rate_percentage DESC;


11.	Which violations are most common among younger drivers (<25)?
select violation,count(*) as total_violations
from traffic_logs
where driver_age<25
group by violation
order by total_violations desc;
12.	Is there a violation that rarely results in search or arrest?
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests,
    ROUND(100.0 * SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_pct
FROM
    traffic_logs
GROUP BY
    violation
HAVING
    ROUND(100.0 * SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) < 5
    AND ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) < 5
ORDER BY
    total_stops DESC;

🌍 Location-Based
13.	Which countries report the highest rate of drug-related stops?
select country_name,count(*) as total_drug_related_stops
from traffic_logs
where drugs_related_stop=True
Group by country_name
order by total_drug_related_stops desc;

14.	What is the arrest rate by country and violation?
select country_name,violation, count(*) as total_stops,
    sum(case when is_arrested = TRUE then 1 else 0 end) as total_arrests,
    round(100.0 * sum(case when is_arrested = TRUE then 1 else 0 end) / count(*),2)as arrest_rate_percentage
from traffic_logs
group by country_name, violation
order by arrest_rate_percentage DESC;
15.	Which country has the most stops with search conducted?
select country_name,count(*) as total_stops
from traffic_logs
where search_conducted=True
group by country_name
order by total_stops desc
limit 3;

(Complex): 
1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)
WITH yearly_stats AS (
    SELECT
        country_name,
        EXTRACT(YEAR FROM stop_date) AS year,
        COUNT(*) AS total_stops,
        SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests
    FROM
        traffic_logs
    GROUP BY
        country_name, EXTRACT(YEAR FROM stop_date)
)

SELECT
    country_name,
    year,
    total_stops,
    total_arrests,
    ROUND(100.0 * total_arrests::NUMERIC / NULLIF(total_stops, 0), 2) AS arrest_rate_pct,
    SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_arrests
FROM
    yearly_stats
ORDER BY
    country_name, year;


2.Driver Violation Trends Based on Age and Race (Join with Subquery)
-- Subquery to aggregate violation counts by age and race
WITH violation_summary AS (
    SELECT
        driver_race,
        CASE 
            WHEN driver_age < 18 THEN 'Under 18'
            WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
            WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
            WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
            ELSE '60+'
        END AS age_group,
        violation,
        COUNT(*) AS violation_count
    FROM
        traffic_logs
    GROUP BY
        driver_race,
        age_group,
        violation
),

-- Subquery to get total stops per age group and race
race_age_totals AS (
    SELECT
        driver_race,
        age_group,
        SUM(violation_count) AS total_violations
    FROM
        violation_summary
    GROUP BY
        driver_race, age_group
)

-- Final join: get percentage of each violation within age/race group
SELECT
    v.driver_race,
    v.age_group,
    v.violation,
    v.violation_count,
    r.total_violations,
    ROUND(100.0 * v.violation_count / r.total_violations, 2) AS percent_of_group
FROM
    violation_summary v
JOIN
    race_age_totals r
ON
    v.driver_race = r.driver_race AND v.age_group = r.age_group
ORDER BY
    v.driver_race, v.age_group, percent_of_group DESC;


3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day
SELECT
    EXTRACT(YEAR FROM stop_date) AS year,
    EXTRACT(MONTH FROM stop_date) AS month,
    EXTRACT(HOUR FROM time_stamp) AS hour,
    COUNT(*) AS total_stops
FROM
    traffic_logs
group by  year, month, hour
ORDER BY year, month, hour;

4.Violations with High Search and Arrest Rates (Window Function)
WITH violation_stats AS (
    SELECT
        violation,
        COUNT(*) AS total_stops,
        SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
        SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
        ROUND(100.0 * SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END)::NUMERIC / COUNT(*), 2) AS search_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::NUMERIC / COUNT(*), 2) AS arrest_rate_pct
    FROM
        traffic_logs
    GROUP BY
        violation
)

SELECT
    *,
    RANK() OVER (ORDER BY search_rate_pct DESC) AS search_rate_rank,
    RANK() OVER (ORDER BY arrest_rate_pct DESC) AS arrest_rate_rank
FROM
    violation_stats
WHERE
    total_stops >= 20 -- optional threshold to filter low-volume violations
ORDER BY
    arrest_rate_pct DESC;


5.Driver Demographics by Country (Age, Gender, and Race)
SELECT
    country_name,
    driver_gender,
    driver_race,
    COUNT(*) AS total_drivers,
    ROUND(AVG(driver_age), 1) AS avg_age,
    MIN(driver_age) AS youngest,
    MAX(driver_age) AS oldest
FROM
    traffic_logs
WHERE
    driver_age IS NOT NULL
GROUP BY
    country_name, driver_gender, driver_race
ORDER BY
    country_name, total_drivers DESC;

6.Top 5 Violations with Highest Arrest Rates
SELECT
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(
        100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::NUMERIC / COUNT(*),
        2
    ) AS arrest_rate_pct
FROM
    traffic_logs
GROUP BY
    violation
ORDER BY
    arrest_rate_pct DESC
LIMIT 5;
