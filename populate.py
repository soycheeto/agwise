import sqlite3
import random
from datetime import datetime, timedelta

# Connect to your database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Drop the existing table if any to start fresh (optional)
cursor.execute('DROP TABLE IF EXISTS sensor_readings')

# Create sensor_readings table with correct columns based on error message
cursor.execute('''
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    soil_moisture REAL,
    temperature REAL,
    wind_speed REAL,
    wind_direction INTEGER,
    light INTEGER,
    uv_index REAL,
    humidity INTEGER,
    pressure INTEGER,
    leaf_moisture INTEGER,
    timestamp TEXT
)
''')

# Generate and insert 50 entries of sensor data
base_time = datetime.now() - timedelta(days=1)
for i in range(50):
    soil_moisture = round(random.uniform(10.0, 40.0), 2)
    temperature = round(random.uniform(15.0, 35.0), 1)
    wind_speed = round(random.uniform(0.0, 15.0), 1)
    wind_direction = random.randint(0, 360)
    light = random.randint(300, 1000)
    uv_index = round(random.uniform(0, 10), 1)
    humidity = random.randint(30, 90)
    pressure = random.randint(980, 1020)
    leaf_moisture = random.randint(10, 50)
    timestamp = (base_time + timedelta(minutes=i * 30)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO sensor_readings (
        soil_moisture, temperature, wind_speed, wind_direction, light, uv_index,
        humidity, pressure, leaf_moisture, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (soil_moisture, temperature, wind_speed, wind_direction, light, uv_index,
          humidity, pressure, leaf_moisture, timestamp))

conn.commit()

# Add code to show inserted entries
print("Inserted 50 entries of sample sensor data. Preview of inserted data:")
cursor.execute('SELECT * FROM sensor_readings')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
