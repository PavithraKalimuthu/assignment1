# assignment1
Traffic logs secure check -Python,SQL & Streamlit

📋 Project Overview:
This project provides a dashboard and backend system to help traffic police units log vehicle stops, analyze data patterns, and visualize metrics like stop frequency, common violations, and location-based trends.

Built using:

- Python
- PostgreSQL 
- Streamlit


Technologies Used:

- Python 3.x
- PostgreSQL
- Streamlit
- SQLAlchemy / psycopg2

  Packages installes and imported:
- Pandas
- Psycopg2
- Streamlit

  Steps:
  - Installed all required packages and imported
  - Loaded the CSV file
  - Data Cleaning- Analysed the CSV file. Checked for duplicated and Nan values
  - Filled the Nan values as missing and there was no duplicates
  - Removed the unwanted columns(driver_age_raw,violation_raw)
  - Analysed the datatypes of each column
  - converted the datatypes
  - Created database named police_logs and pushed the cleaned data to Sql(police_logs) db.
  - In a new py file, imported required packages
  - created the Connection between python to police_logs database
  - Fetched the data from the database
  - written codes to visualise the entire project and the queries written
