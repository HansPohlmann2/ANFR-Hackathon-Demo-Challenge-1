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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df_test = pd.read_csv("resultats/attenuation_estimee_testset.csv")
df_base = pd.read_csv("resultats/pci_associes_infos_corriges.csv", low_memory=False)
df_base = df_base.rename(columns={"latitude": "Latitude", "longitude": "Longitude"})
df = pd.merge(df_test, df_base, on=["Latitude", "Longitude"], how="left")
df = df.dropna(subset=["Latitude", "Longitude", "tm_dbm"])

plt.figure(figsize=(10, 8))
sc = plt.scatter(
    df["Longitude"],
    df["Latitude"],
    c=df["tm_dbm"],
    cmap="viridis",
    s=10,
    alpha=0.7,
    rasterized=True,
    vmin=-120,
    vmax=-30
)
plt.colorbar(sc, label="Pmes (dBm)")
plt.title("Carte géographique de la Pmes")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("visualisations/graph3_carte_geographique_pmes.png")
plt.close()
