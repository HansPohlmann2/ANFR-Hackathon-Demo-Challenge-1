
# MIT License
#
# Copyright (c) 2025 Mathieu Witkowski, Clément Poucet, Hans Pohlmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas as pd
import polars as pl
import numpy as np
from scipy.spatial import KDTree, Voronoi, voronoi_plot_2d
from math import atan2, degrees, radians, sin, cos, sqrt
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import defaultdict

# === PARAMÈTRES GLOBAUX ===
N_LIGNES_MESURES = None  # None = tout traiter, ou mettre un entier (ex: 20000)

# === FONCTIONS ===
def angle_between_points(lat1, lon1, lat2, lon2):
    return (degrees(atan2(lat2 - lat1, lon2 - lon1)) + 360) % 360

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# === SUPPORT ===
df_support = pl.read_csv(
    "ressources\\SUPPORT_clean.csv",
    separator=";",
    columns=["STA_NM_ANFR", "LAT_DECIMAL", "LON_DECIMAL"],
    schema_overrides={"STA_NM_ANFR": pl.Utf8}
).with_columns([
    pl.col("LAT_DECIMAL").str.replace(",", ".").cast(pl.Float64).alias("LAT"),
    pl.col("LON_DECIMAL").str.replace(",", ".").cast(pl.Float64).alias("LON")
]).filter(
    (pl.col("LAT") >= 42) & (pl.col("LAT") <= 52) &
    (pl.col("LON") >= -5) & (pl.col("LON") <= 9)
)

support_coords = df_support.select(["LAT", "LON"]).to_numpy()
support_tree = KDTree(support_coords)
support_labels = df_support.select(["STA_NM_ANFR", "LAT", "LON"]).to_pandas()

# === ANTENNES ===
df_antennes = pl.read_csv(
    "ressources\\ANTENNE_clean.csv",
    separator=";",
    columns=["STA_NM_ANFR", "AER_ID", "AER_NB_AZIMUT"],
    schema_overrides={"STA_NM_ANFR": pl.Utf8, "AER_ID": pl.Utf8}
).with_columns([
    pl.col("AER_NB_AZIMUT").str.replace(",", ".").cast(pl.Float64)
])
antennes_pd = df_antennes.to_pandas()
antenne_map = defaultdict(list)
for _, row in antennes_pd.iterrows():
    antenne_map[row["STA_NM_ANFR"]].append(row)

# === EMETTEURS ===
df_emetteur = pl.read_csv(
    "ressources\\EMETTEUR_clean.csv",
    separator=";",
    columns=["STA_NM_ANFR", "AER_ID", "EMR_NB_PUISSANCE"],
    schema_overrides={"STA_NM_ANFR": pl.Utf8, "AER_ID": pl.Utf8, "EMR_NB_PUISSANCE": pl.Utf8}
).with_columns([
    pl.col("EMR_NB_PUISSANCE").str.replace(",", ".").cast(pl.Float64)
])
emetteurs_pd = df_emetteur.to_pandas()
emetteur_lookup = emetteurs_pd.set_index(["STA_NM_ANFR", "AER_ID"])["EMR_NB_PUISSANCE"].to_dict()

# === MESURES ===
df_mesures = pl.read_csv(
    "ressources\\Mesures_clean.csv",
    separator=";",
    columns=["latitude", "longitude", "tm_cid", "tm_dbm", "pci", "band_table"],
    schema_overrides={
        "latitude": pl.Utf8,
        "longitude": pl.Utf8,
        "tm_dbm": pl.Utf8,
        "tm_cid": pl.Utf8,
        "pci": pl.Utf8,
        "band_table": pl.Utf8
    }
).with_columns([
    pl.col("latitude").str.replace(",", ".").cast(pl.Float64),
    pl.col("longitude").str.replace(",", ".").cast(pl.Float64),
    pl.col("tm_dbm").str.replace(",", ".").cast(pl.Float64)
]).filter(
    (pl.col("latitude") >= 42) & (pl.col("latitude") <= 52) &
    (pl.col("longitude") >= -5) & (pl.col("longitude") <= 9)
)

if N_LIGNES_MESURES is not None:
    df_mesures = df_mesures.slice(0, N_LIGNES_MESURES)

mesures_pd = df_mesures.to_pandas()
mesure_coords = df_mesures.select(["latitude", "longitude"]).to_numpy()
_, indices = support_tree.query(mesure_coords)
support_matched = support_labels.iloc[indices].reset_index(drop=True)

# === ASSOCIATION ANTENNE + PUISSANCE ===
results = []
print("Association en cours...")

for i, row in tqdm(mesures_pd.iterrows(), total=len(mesures_pd)):
    lat, lon = row["latitude"], row["longitude"]
    tm_cid, tm_dbm, pci, band_table = row["tm_cid"], row["tm_dbm"], row["pci"], row["band_table"]
    support = support_matched.iloc[i]
    sta_nm = support["STA_NM_ANFR"]

    antennes = antenne_map.get(sta_nm, [])
    if not antennes:
        continue

    angle = angle_between_points(support["LAT"], support["LON"], lat, lon)
    distance = haversine(lat, lon, support["LAT"], support["LON"])

    azimuts = [a["AER_NB_AZIMUT"] for a in antennes if not pd.isna(a["AER_NB_AZIMUT"])]
    if not azimuts:
        continue

    angle_diffs = np.abs((np.array(azimuts) - angle + 180) % 360 - 180)
    idx_min = np.argmin(angle_diffs)
    best_antenne = antennes[idx_min]
    aer_id = best_antenne["AER_ID"]
    puissance = emetteur_lookup.get((sta_nm, aer_id), np.nan)

    results.append({
        "latitude": lat,
        "longitude": lon,
        "tm_cid": tm_cid,
        "tm_dbm": tm_dbm,
        "pci": pci,
        "band_table": band_table,
        "STA_NM_ANFR": sta_nm,
        "AER_ID": aer_id,
        "AER_NB_AZIMUT": best_antenne["AER_NB_AZIMUT"],
        "angle_vers_antenne": angle,
        "distance_to_support_km": round(distance, 3),
        "EMR_NB_PUISSANCE": puissance,
    })

# === Correction logique : rattachement du tm_cid à la station majoritaire ===
df_result = pd.DataFrame(results)
dominantes = df_result.groupby(["tm_cid", "STA_NM_ANFR"]).size().reset_index(name="count")
dominantes = dominantes.sort_values(["tm_cid", "count"], ascending=[True, False])
dominantes_unique = dominantes.drop_duplicates("tm_cid").set_index("tm_cid")["STA_NM_ANFR"].to_dict()
df_result["STA_NM_ANFR"] = df_result["tm_cid"].map(dominantes_unique)

# === EXPORT CSV ===
df_result.to_csv("resultats\\pci_associes_infos_corriges.csv", index=False)
print("✅ Export terminé : pci_associes_infos_corriges.csv")

# === VORONOI CLEAN ===
print("Affichage Voronoi...")
points = df_support.select(["LON", "LAT"]).to_numpy()
points = np.unique(points, axis=0)
vor = Voronoi(points)

fig, ax = plt.subplots(figsize=(10, 10))
voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='black', line_width=0.6, point_size=1)
ax.plot(points[:, 0], points[:, 1], 'ro', markersize=1, label="Supports")
ax.plot(mesures_pd["longitude"], mesures_pd["latitude"], 'bo', markersize=2, alpha=0.3, label="Mesures")
ax.set_title("Voronoi (corrigé par tm_cid)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()


