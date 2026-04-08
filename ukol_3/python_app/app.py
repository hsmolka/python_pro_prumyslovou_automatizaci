import pprint
import requests
from datetime import datetime
import csv
import urllib3
import mysql.connector
import time
import os
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# souřadnice Pradědu
LAT = 50.0831
LON = 17.2310

START_DATE = "1950-01-01"
END_DATE = "2024-12-31"

# získání dat
def get_weather(lat: float, lon: float, start_date: str, end_date: str):
    url = "https://archive-api.open-meteo.com/v1/archive"
    parameters = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "Europe/Prague",
    }
    pprint.pprint(parameters)
    try:
        print("Získávám data z Open-Meteo...")
        response = requests.get(url, params=parameters, timeout=30, verify=False)
        if response.status_code == 200:
            print("Úspěšné získání dat")
            return response.json()
        else:
            error = response.json()
            print(f"API Error {response.status_code}: {error.get('reason', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Chyba požadavku: {e}")
        return None

# uložení dat do CSV
def save_to_csv(data):
    daily = data["daily"]
    dates = daily["time"]
    temps_max = daily["temperature_2m_max"]
    temps_min = daily["temperature_2m_min"]

    with open("data.csv", "w", newline="") as file:
        zapis = csv.writer(file)
        zapis.writerow(["date", "temp_max", "temp_min"])
        for date, tmax, tmin in zip(dates, temps_max, temps_min):
            zapis.writerow([date, tmax, tmin])
    print("Uloženo jako data.csv")

# čtení a transformace dat z CSV
def read_csv():
    rows = []
    with open("data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "date": row["date"],
                "temp_max": float(row["temp_max"]) if row["temp_max"] != "" else None,
                "temp_min": float(row["temp_min"]) if row["temp_min"] != "" else None,
            })
    print(f"Načteno {len(rows)} řádků z CSV")
    return rows

# připojení k MariaDB s opakovanými pokusy
def connect_db():
    db_host = os.environ.get("DB_HOST", "mariadb-container")
    for attempt in range(10):
        try:
            print(f"Připojuji se k MariaDB na {db_host} (pokus {attempt+1})...")
            conn = mysql.connector.connect(
                host=db_host,
                user=os.environ.get("DB_USER", "user123"),
                password=os.environ.get("DB_PASSWORD", "pass123"),
                database=os.environ.get("DB_NAME", "mydb")
            )
            print("Připojeno!")
            return conn
        except Exception as e:
            print(f"Není připraveno: {e}")
            time.sleep(5)
    raise Exception("Nepodařilo se připojit k MariaDB po 10 pokusech")

# uložení dat do MariaDB
def insert_data(conn, rows):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            temp_max FLOAT,
            temp_min FLOAT
        )
    """)
    cursor.execute("DELETE FROM weather")
    for row in rows:
        cursor.execute(
            "INSERT INTO weather (date, temp_max, temp_min) VALUES (%s, %s, %s)",
            (row["date"], row["temp_max"], row["temp_min"])
        )
    conn.commit()
    print(f"Vloženo {len(rows)} řádků do MariaDB")
    cursor.close()

def main():
    data = get_weather(LAT, LON, START_DATE, END_DATE)
    if data is None:
        print("Chyba: nepodařilo se získat data")
        return
    save_to_csv(data)
    rows = read_csv()
    conn = connect_db()
    insert_data(conn, rows)
    conn.close()
    print("Hotovo!")

if __name__ == "__main__":
    main()