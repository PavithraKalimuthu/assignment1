import psycopg2
import pandas as pd
import streamlit as st

def create_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="policelogs",
            user= "postgres",
            password="Apple123"
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=colnames)
                return df
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return pd.DataFrame()
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    
#streamlit UI
st.set_page_config(page_title="Police SecureCheck Dashboard",layout="wide")
st.title('SecureWatch – "Your Patrol, Your Record."🛡️🚓')
st.markdown("🕵️From Streets to Systems: Real-Time Security Logging.")

#viewing full records:
st.header("🗃️ Police logs Overview")
query="Select * from traffic_logs"
data=fetch_data(query)
st.dataframe(data,use_container_width=True)

#key metrics
st.header("Key Metrics📊")
col1,col2,col3,col4=st.columns(4)

with col1:
    total_stops=data.shape[0]
    st.metric("🛑Total Police Stops",total_stops)
with col2:
    total_arrests=data[data['stop_outcome'].str.contains("arrest",case=False,na=False)].shape[0]
    st.metric("🔗Total Arrests",total_arrests)
with col3:
    warnings=data[data['stop_outcome'].str.contains("warning",case=False,na=False)].shape[0]
    st.metric("❗Total Warnings",warnings)
with col4:
    drug=data[data['drugs_related_stop']==True]
    st.metric("🚱No of Drug Related Stops",len(drug))
#Changing background
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("http://cdn.wallpapersafari.com/69/19/BxLop0.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#Advanced Queries
st.header("🔍Advanced Insights")
Selected_query=st.selectbox("📌Select a Query to Run",[
    "🚗Top 10 vehicle_Number involved in drug-related stops",
    "🚗Most frequently searched Vechicle",
    "🧍Driver age Group with highest arrest rate",
    "🧍Gender distribution of drivers stopped in each country",
    "🧍Highest search rate by race and gender"
    "🕒Time of the day sees most traffic stops",
    "🕒Average stop duration for different violations",
    "🕒stops during the night-leads to arrests?",
    "⚖️Violations most associated with searches or arrests",
    "⚖️violation most among drivers under 25",
    "⚖️violation that rarely results in search or arrest",
    "🧭Country that has highest drug related stops",
    "🧭Arrest rate by country and violation",
    "🧭country that has most search conducted stops",
    "💡Yearly Breakdown of Stops and Arrests by Country ",
    "💡Driver Violation Trends Based on Age and Race ",
    "💡Time Period Analysis of Stops",
    "💡Violations with High Search and Arrest Rates ",
    "💡Driver Demographics by Country ",
    "💡Top 5 Violations with Highest Arrest Rates"
    

])

query_map={
     "🚗Top 10 vehicle_Number involved in drug-related stops":"Select vehicle_number,count(*)as stop_counts from traffic_logs where drugs_related_stop=True group by vehicle_number order by stop_counts DESC limit 10",
     "🚗Most frequently searched Vechicle":"select vehicle_number, count(*)as search_count from traffic_logs where search_conducted = TRUE group by vehicle_number order by search_count DESC LIMIT 10",
     "🧍Driver age Group with highest arrest rate":"select driver_age, count(*) as arrest_count from traffic_logs where is_arrested = TRUE group by driver_age order by arrest_count DESC LIMIT 3",
     "🧍Gender distribution of drivers stopped in each country":"select driver_gender,country_name,count(*) as stop_counts from traffic_logs group by country_name,driver_gender order by country_name,driver_gender",
     "🧍Highest search rate by race and gender":"select driver_race,driver_gender,count(*)as total_stops,round(100*sum(case when search_conducted=True then 1 else 0 end)/count(*),2) as search_rate_percentage from traffic_logs Group by driver_race, driver_gender order by search_rate_percentage DESC limit 1",
     "🕒Time of the day sees most traffic stops":"SELECT CASE WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 5 AND 11 THEN 'Morning' WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 12 AND 16 THEN 'Afternoon' WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 17 AND 20 THEN 'Evening' ELSE 'Night' END AS time_of_day, COUNT(*) AS stop_count FROM traffic_logs GROUP BY time_of_day ORDER BY stop_count DESC",
     "🕒Average stop duration for different violations":"select violation, round(avg(case stop_duration when '<15 min' then 7 when '16-30 min' then 23 when '30+ min' then 40 else null end), 2) as avg_stop_duration_minutes from traffic_logs group by violation order by avg_stop_duration_minutes desc",
     "🕒stops during the night-leads to arrests?":"select case when stop_time >= '20:00:00' or stop_time < '06:00:00' then 'night' else 'day' end as time_of_day, count(*) as total_stops, sum(case when is_arrested = true then 1 else 0 end) as arrests, round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) as arrest_rate_percentage from traffic_logs group by time_of_day",
     "⚖️Violations most associated with searches or arrests":"select violation, count(*) as total_stops, sum(case when search_conducted = true then 1 else 0 end) as total_searches, sum(case when is_arrested = true then 1 else 0 end) as total_arrests, round(100.0 * sum(case when search_conducted = true then 1 else 0 end) / count(*), 2) as search_rate_percentage, round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) as arrest_rate_percentage from traffic_logs group by violation order by arrest_rate_percentage desc, search_rate_percentage desc",
     "⚖️violation most among drivers under 25":"select violation, count(*) as total_violations from traffic_logs where driver_age < 25 group by violation order by total_violations desc",
     "⚖️violation that rarely results in search or arrest":"select violation, count(*) as total_stops, sum(case when search_conducted = true then 1 else 0 end) as searches, sum(case when is_arrested = true then 1 else 0 end) as arrests, round(100.0 * sum(case when search_conducted = true then 1 else 0 end) / count(*), 2) as search_rate_pct, round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) as arrest_rate_pct from traffic_logs group by violation having round(100.0 * sum(case when search_conducted = true then 1 else 0 end) / count(*), 2) < 5 and round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) < 5 order by total_stops desc",
     "🧭Country that has highest drug related stops":"select country_name, count(*) as total_drug_related_stops from traffic_logs where drugs_related_stop = true group by country_name order by total_drug_related_stops desc",
     "🧭Arrest rate by country and violation":"select country_name, violation, count(*) as total_stops, sum(case when is_arrested = true then 1 else 0 end) as total_arrests, round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) as arrest_rate_percentage from traffic_logs group by country_name, violation order by arrest_rate_percentage desc",
     "🧭country that has most search conducted stops":"select country_name, count(*) as total_stops from traffic_logs where search_conducted = true group by country_name order by total_stops desc limit 3",
     "💡Yearly Breakdown of Stops and Arrests by Country ":"with yearly_stats as (select country_name, extract(year from stop_date) as year, count(*) as total_stops, sum(case when is_arrested = true then 1 else 0 end) as total_arrests from traffic_logs group by country_name, extract(year from stop_date)) select country_name, year, total_stops, total_arrests, round(100.0 * total_arrests::numeric / nullif(total_stops, 0), 2) as arrest_rate_pct, sum(total_arrests) over (partition by country_name order by year rows between unbounded preceding and current row) as cumulative_arrests from yearly_stats order by country_name, year",
     "💡Driver Violation Trends Based on Age and Race ":"with violation_summary as (select driver_race, case when driver_age < 18 then 'under 18' when driver_age between 18 and 25 then '18-25' when driver_age between 26 and 40 then '26-40' when driver_age between 41 and 60 then '41-60' else '60+' end as age_group, violation, count(*) as violation_count from traffic_logs group by driver_race, age_group, violation), race_age_totals as (select driver_race, age_group, sum(violation_count) as total_violations from violation_summary group by driver_race, age_group) select v.driver_race, v.age_group, v.violation, v.violation_count, r.total_violations, round(100.0 * v.violation_count / r.total_violations, 2) as percent_of_group from violation_summary v join race_age_totals r on v.driver_race = r.driver_race and v.age_group = r.age_group order by v.driver_race, v.age_group, percent_of_group desc",
     "💡Time Period Analysis of Stops":"select extract(year from stop_date) as year, extract(month from stop_date) as month, extract(hour from time_stamp) as hour, count(*) as total_stops from traffic_logs group by year, month, hour order by year, month, hour",
     "💡Violations with High Search and Arrest Rates ":"with violation_stats as (select violation, count(*) as total_stops, sum(case when search_conducted = true then 1 else 0 end) as total_searches, sum(case when is_arrested = true then 1 else 0 end) as total_arrests, round(100.0 * sum(case when search_conducted = true then 1 else 0 end)::numeric / count(*), 2) as search_rate_pct, round(100.0 * sum(case when is_arrested = true then 1 else 0 end)::numeric / count(*), 2) as arrest_rate_pct from traffic_logs group by violation) select *, rank() over (order by search_rate_pct desc) as search_rate_rank, rank() over (order by arrest_rate_pct desc) as arrest_rate_rank from violation_stats where total_stops >= 20 order by arrest_rate_pct desc",
     "💡Driver Demographics by Country ":"select country_name, driver_gender, driver_race, count(*) as total_drivers, round(avg(driver_age), 1) as avg_age, min(driver_age) as youngest, max(driver_age) as oldest from traffic_logs where driver_age is not null group by country_name, driver_gender, driver_race order by country_name, total_drivers desc",
     "💡Top 5 Violations with Highest Arrest Rates":"select violation, count(*) as total_stops, sum(case when is_arrested = true then 1 else 0 end) as total_arrests, round(100.0 * sum(case when is_arrested = true then 1 else 0 end)::numeric / count(*), 2) as arrest_rate_pct from traffic_logs group by violation order by arrest_rate_pct desc limit 5"
    
    
}
if st.button("▶️Run Query"):
    result=fetch_data(query_map[Selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("☹️No Result Found")

st.markdown("__________")
st.markdown("🫡Data on Duty")

st.header("🧾 Add New Log & Predict Outcome and Violation")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["Male", "Female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was Search Conducted", ["0", "1"])
    search_type = st.text_input("Search Type")
    stop_duration = st.text_input("Stop Duration")
    drugs_related_stop = st.selectbox("Was it a Drug-Related Stop?", ["0", "1"])
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("🔍 Predict Stop Outcome and Violation")

if submitted:
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data['drugs_related_stop'] == int(drugs_related_stop))
    ]

    # Predict stop outcome and violation
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "Warning"
        predicted_violation = "Speeding"

    # Descriptive text
    search_text = "a search was conducted" if int(search_conducted) else "no search was conducted"
    drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

    # Display result
    st.markdown(f"""
### 📋 Prediction Summary

**🚦 Predicted Violation:** `{predicted_violation}`  
**📢 Predicted Stop Outcome:** `{predicted_outcome}`  

🧾On **{stop_date}** at **{stop_time.strftime("%H:%M:%S")}**, a **{driver_age}**-year-old **{driver_gender}** driver was stopped in **{country_name}**.  
The traffic stop **{drug_text}**, and **{search_text}**.  
The stop lasted for **"{stop_duration}"**, and the vehicle number was **{vehicle_number}**.

""")