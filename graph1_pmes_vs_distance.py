

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
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import re

def extract_max_freq(text):
    if pd.isna(text):
        return None
    numbers = re.findall(r"\d+", str(text))
    return max(map(int, numbers)) if numbers else None

df_test = pd.read_csv("resultats/attenuation_estimee_testset.csv")
df_base = pd.read_csv("resultats/pci_associes_infos_corriges.csv", low_memory=False)
df_type = pd.read_csv("resultats/type_de_milieu_par_point.csv", sep=";")

df_base = df_base.rename(columns={"latitude": "Latitude", "longitude": "Longitude"})
df = pd.merge(df_test, df_base, on=["Latitude", "Longitude"], how="left")
df = pd.merge(df, df_type[["STA_NM_ANFR", "TYPE"]], on="STA_NM_ANFR", how="left")

df = df.dropna(subset=["Latitude", "Longitude", "tm_dbm", "distance_to_support_km"])

df["frequence"] = df["band_table"].apply(extract_max_freq)
df["frequence"] = pd.to_numeric(df["frequence"], errors="coerce")

df_plot = df[df["distance_to_support_km"] <= 30]
if len(df_plot) > 20000:
    df_plot = df_plot.sample(20000, random_state=42)

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_plot,
    x="distance_to_support_km",
    y="tm_dbm",
    hue="TYPE",
    alpha=0.6,
    rasterized=True
)
plt.ylim(-120, -30)
plt.title("Puissance mesurée (Pmes) vs Distance (≤ 30 km)")
plt.xlabel("Distance (km)")
plt.ylabel("Pmes (dBm)")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.savefig("visualisations/graph1_pmes_vs_distance.png")
plt.close()


