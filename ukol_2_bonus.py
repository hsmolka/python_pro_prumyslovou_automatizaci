import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

#Načtení dat
URL = "https://data.csu.gov.cz/api/dotaz/v1/data/vybery/CRUHVD1T2?format=CSV"
response = requests.get(URL)
response.raise_for_status()

df = pd.read_csv(URL, encoding="utf-8")

#vyčištění dat
df.columns = (df.columns.str.strip().str.strip('"').str.replace("\ufeff", "", regex=False))
if len(df.columns) == 5:
    df.columns = ["ukazatel", "rok", "region", "rezidence", "hodnota"]
else:
    raise ValueError(f"Expected 5 columns, got {len(df.columns)}: {df.columns.tolist()}")

#filtr dat
df["hodnota"] = pd.to_numeric(df["hodnota"], errors="coerce")
df = df.dropna(subset=["hodnota"])

#Jeden ukazatel only
ukazatel_val = df["ukazatel"].iloc[0]
df = df[df["ukazatel"] == ukazatel_val]

# Drop national total
df = df[~df["region"].isin(["Česká republika", "ČR"])]

# Přepis krajů
region_map = {
    "Středočeský kraj":   "Středočeský",
    "Jihočeský kraj":     "Jihočeský",
    "Plzeňský kraj":      "Plzeňský",
    "Karlovarský kraj":   "Karlovarský",
    "Ústecký kraj":       "Ústecký",
    "Liberecký kraj":     "Liberecký",
    "Královéhradecký kraj": "Královéhrad.",
    "Pardubický kraj":    "Pardubický",
    "Kraj Vysočina":      "Vysočina",
    "Jihomoravský kraj":  "Jihomoravský",
    "Olomoucký kraj":     "Olomoucký",
    "Zlínský kraj":       "Zlínský",
    "Moravskoslezský kraj": "Mor.-slezský",
    "Praha":              "Praha",
    "Moravskoslezsko":    "Mor.-slezsko",
}
df["region_short"] = df["region"].map(region_map).fillna(df["region"])


agg = df.groupby(["region_short", "rezidence"], as_index=False)["hodnota"].sum()

# Seřazení podle hodnot
order = (
    agg[agg["rezidence"] == "Celkem"]
    .sort_values("hodnota", ascending=False)["region_short"]
    .tolist()
)
#plot
palette   = {"Celkem": "#4C72B0", "Rezidenti": "#55A868", "Nerezidenti": "#C44E52"}
hue_order = ["Celkem", "Rezidenti", "Nerezidenti"]

fig, ax = plt.subplots(figsize=(18, 7))

sns.barplot(
    data=agg,
    x="region_short",
    y="hodnota",
    hue="rezidence",
    order=order,
    hue_order=hue_order,
    palette=palette,
    edgecolor="white",
    linewidth=0.6,
    ax=ax,
)

ax.set_title(f"Cestovní ruch 2024 – {ukazatel_val} podle regionů",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Region / kraj", fontsize=11)
ax.set_ylabel("Počet", fontsize=11)
ax.tick_params(axis="x", rotation=40, labelsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{int(x):,}".replace(",", "\u202f")
))
ax.legend(title="Rezidence", fontsize=9, title_fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.4)
sns.despine(ax=ax)
plt.tight_layout()

#uložení
out_path = "graf.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"Uloženo jako {out_path}")
plt.show()