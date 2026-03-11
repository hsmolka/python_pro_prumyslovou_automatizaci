import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


#data z termokamery, smazání prvních 6 řádků - obsahují hlavičku, enconding pro windows, použita desetinná čárka
file = pd.read_csv("temp.dat",sep="\t", skiprows=6,encoding='cp1252', decimal=',')

#převod času - sloupec Time je string a obsahuje ":" jako oddělovac
file = file[file["Time"].str.contains(":")]
#str formát do času H:M:S, přidání sloupce Time v2 - bohužel to přidá in rok Jan 1, 1900 - seaborn to nezobrazí, u Plotly vyřešeno přes update xaxes
file["Time v2"] = pd.to_datetime(file["Time"], format="%H:%M:%S,%f")
print(file)
#preskocit data menši nez 600 - výsledky jsou dulezite od 600°C nahoru
skip = (file["Area 1"] >= 600).idxmax()
skip_file = file.iloc[skip:]

#graf, Area 1 - naměřená teplota
sns.lineplot(data=skip_file, x="Time v2", y="Area 1")

plt.xlabel("Time (seconds)")
plt.ylabel("Temperature °C")
plt.show()

#plotly
fig = px.scatter(
    skip_file,
    x="Time v2",
    y="Area 1",
    color="Area 1",
    size_max=15,
    title="Thermo camera data",
    labels={"Time v2": "Time: hours:minutes:seconds,miliseconds", "Area 1": "Temperature °C"}
)
#vymazání roku 1901, použití pouze formátu H:M:S:mS
fig.update_xaxes(tickformat="%H:%M:%S,%f", dtick=1*60000)

fig.show()

