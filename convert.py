import sqlite3
import pandas as pd

# Connect to the existing SQLite database
conn = sqlite3.connect('sensor_data.db')

# Read the sensor_readings table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM sensor_readings", conn)

# Export the DataFrame to a CSV file
df.to_csv('sensor_data.csv', index=False)

conn.close()

print("Converted sensor_readings table from sensor_data.db into sensor_data.csv")
