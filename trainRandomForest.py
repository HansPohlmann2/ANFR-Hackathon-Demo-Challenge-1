
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
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# === CHARGEMENT DES DONNÉES ===

df = pd.read_csv("resultats\\pci_associes_infos_corriges.csv", sep=",", low_memory=False)
df_gain = pd.read_csv("ressources\\Gain.csv", sep=";")
df_milieu = pd.read_csv("resultats\\type_de_milieu_par_point.csv", sep=";")

# === DÉTECTION DES COLONNES COORDONNÉES ===

lat_col = [c for c in df.columns if "lat" in c.lower()][0]
lon_col = [c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()][0]

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

# === ATTENUATION ===

df["ATT_estimee"] = df["EMR_NB_PUISSANCE"] + df["Gr"] - df["tm_dbm"]

# === ENCODAGE TYPE ===

df_encoded = pd.get_dummies(df, columns=["TYPE"], drop_first=True)

# === SPLIT 80/20 (RÉINITIALISÉ) ===

df_encoded = df_encoded.sample(frac=1, random_state=42).reset_index(drop=True)
split_index = int(0.8 * len(df_encoded))
df_train = df_encoded.iloc[:split_index]
df_test = df_encoded.iloc[split_index:]

# === FEATURES ===

base_features = [
    "distance_to_support_km",
    "frequence",
    "EMR_NB_PUISSANCE",
    "Gr",
    "angle_vers_antenne",
]
type_features = [col for col in df_encoded.columns if col.startswith("TYPE_")]
features = base_features + type_features

X_train = df_train[features]
y_train = df_train["ATT_estimee"]

# === ENTRAÎNEMENT ===

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === ÉVALUATION ===

X_test_eval = df_test[features]
y_test_eval = df_test["ATT_estimee"]
y_pred = model.predict(X_test_eval)

print("R² :", round(r2_score(y_test_eval, y_pred), 3))
print("RMSE :", round(np.sqrt(mean_squared_error(y_test_eval, y_pred)), 2))

# === EXPORT DU MODÈLE ===

joblib.dump(model, "resultats\\random_forest_att_model.pkl")
print("Modèle sauvegardé : random_forest_att_model.pkl")

# === EXPORT DU TEST SET AVEC COORDONNÉES ===

coords = df[[lat_col, lon_col]].reset_index(drop=True)
df_test_export = df_test.copy()
df_test_export["Latitude"] = coords.iloc[df_test.index][lat_col].values
df_test_export["Longitude"] = coords.iloc[df_test.index][lon_col].values
df_test_export[features + ["Latitude", "Longitude"]].to_csv("resultats\\data_testset_for_heatmap.csv", index=False)
print("Test set sauvegardé : data_testset_for_heatmap.csv")
