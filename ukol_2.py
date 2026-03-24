import pprint
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import urllib3
import seaborn as sns
from collections import defaultdict
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# souřadnice Pradědu
LAT = 50.0831
LON = 17.2310
""" Olomouc
LAT = 49.5938
LON = 17.2509
"""

# datum od kdy do kdy
START_DATE = "1950-01-01"
END_DATE = "2024-12-31"

#získání dat
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

#nastavení formátu data
def format_date(date_string: list):
    return [datetime.strptime(d, "%Y-%m-%d") for d in date_string]

#uložení dat
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

#plot grafu
def plot_yearly_minmax(data):
    daily = data["daily"]
    dates = format_date(daily["time"])
    temps_max = daily["temperature_2m_max"]
    temps_min = daily["temperature_2m_min"]

    yearly_max = defaultdict(list)
    yearly_min = defaultdict(list)

    for date, tmax, tmin in zip(dates, temps_max, temps_min):
        if tmax is not None and tmin is not None:
            yearly_max[date.year].append(tmax)
            yearly_min[date.year].append(tmin)

    years = sorted(yearly_max.keys())
    yearly_max_vals = [max(yearly_max[y]) for y in years]
    yearly_min_vals = [min(yearly_min[y]) for y in years]
#vzhled
    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(16, 6))

    ax.plot(years, yearly_max_vals, color="red",  linewidth=2.0, marker="o", label="Roční maximum")
    ax.plot(years, yearly_min_vals, color="blue", linewidth=2.0, marker="o", label="Roční minimum")
    ax.fill_between(years, yearly_min_vals, yearly_max_vals, alpha=0.15, color="grey")
    plt.xticks(rotation=45)
#popisy grafu
    ax.set_xlabel("Rok")
    ax.set_ylabel("Teplota (°C)")
    ax.set_title("Roční min a max teploty na Pradědu")
    ax.legend()
    plt.tight_layout()
    plt.show()


def main():
    data = get_weather(LAT, LON, START_DATE, END_DATE)
    save_to_csv(data)
    plot_yearly_minmax(data)



if __name__ == "__main__":
    main()