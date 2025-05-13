
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
import joblib

# === CHARGEMENT DES DONNÉES ===

df = pd.read_csv("resultats\\pci_associes_infos_kdtree_final.csv", sep=",", low_memory=False)
df_gain = pd.read_csv("ressources\\Gain.csv", sep=";")
df_milieu = pd.read_csv("resultats\\type_de_milieu_par_point.csv", sep=";")

# === DÉTECTION DES COLONNES DE COORDONNÉES ===

possible_lat_names = [col for col in df.columns if "lat" in col.lower()]
possible_lon_names = [col for col in df.columns if "lon" in col.lower() or "lng" in col.lower()]

if not possible_lat_names or not possible_lon_names:
    raise ValueError("Impossible de détecter les colonnes Latitude/Longitude.")

lat_col = possible_lat_names[0]
lon_col = possible_lon_names[0]

# === AJOUT FREQUENCE + GAIN ===

df["frequence"] = df["band_table"].astype(str).str.extract(r"(\d+)")[0]
df = df[df["frequence"].notna()]
df["frequence"] = df["frequence"].astype(int)

gain_dict = dict(zip(df_gain["Frequence"], df_gain["Gain"]))
df["Gr"] = df["frequence"].map(gain_dict)

# === AJOUT TYPE DE MILIEU ===

df = df.merge(df_milieu[["STA_NM_ANFR", "TYPE"]], on="STA_NM_ANFR", how="left")

# === NETTOYAGE ===

df = df.dropna(subset=[
    "tm_dbm", "EMR_NB_PUISSANCE", "Gr", "TYPE",
    "distance_to_support_km", "angle_vers_antenne", lat_col, lon_col
])

# === CALCUL ATTENUATION ===

df["ATT_estimee"] = df["EMR_NB_PUISSANCE"] + df["Gr"] - df["tm_dbm"]

# === ENCODAGE TYPE ===

df_encoded = pd.get_dummies(df, columns=["TYPE"], drop_first=True)

# === SPLIT 80/20 ===

df_encoded_shuffled = df_encoded.sample(frac=1, random_state=42).reset_index(drop=True)
split_index = int(0.8 * len(df_encoded_shuffled))

df_test = df_encoded_shuffled.iloc[split_index:]

# === FEATURES COMME À L’ENTRAÎNEMENT ===

base_features = [
    "distance_to_support_km",
    "frequence",
    "EMR_NB_PUISSANCE",
    "Gr",
    "angle_vers_antenne",
]

type_features = [col for col in df_test.columns if col.startswith("TYPE_")]
all_features = base_features + type_features

# === CHARGEMENT DU MODÈLE ===

model = joblib.load("resultats\\random_forest_att_model.pkl")

# === PRÉPARATION DES DONNÉES TEST ===

for col in model.feature_names_in_:
    if col not in df_test.columns:
        df_test[col] = 0

X_test = df_test[model.feature_names_in_]

# === COORDONNÉES DU TEST SET ===

coords = df[[lat_col, lon_col]].reset_index(drop=True)
df_test_coords = coords.iloc[df_test.index].reset_index(drop=True)

# === PRÉDICTION ===

df_test_coords["ATT_estimee"] = model.predict(X_test)

# === EXPORT CSV ===

df_test_coords.rename(columns={lat_col: "Latitude", lon_col: "Longitude"}, inplace=True)
df_test_coords.to_csv("resultats\\attenuation_estimee_testset.csv", index=False)
print("Résultats exportés : attenuation_estimee_testset.csv")
