
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

# Charger les fichiers (avec le bon séparateur pour Gain.csv)
gain_df = pd.read_csv("ressources\\Gain.csv", sep=";")
att_df = pd.read_csv("resultats\\attenuation_estimee_testset.csv", sep=",")
pci_df = pd.read_csv("resultats\\pci_associes_infos_corriges.csv", sep=",")

# Nettoyage des noms de colonnes
gain_df.columns = gain_df.columns.str.strip()
att_df.columns = att_df.columns.str.strip()
pci_df.columns = pci_df.columns.str.strip()

# Vérification colonnes (debug)
print("Colonnes Gain.csv :", gain_df.columns.tolist())

# Fusion des coordonnées pour ajouter ATT_estimee
df = pci_df.merge(att_df, left_on=["latitude", "longitude"], right_on=["Latitude", "Longitude"], how="left")

# Extraction de la fréquence depuis band_table
def extract_frequency(band_str):
    if pd.isna(band_str):
        return None
    for freq in gain_df['Frequence']:
        if str(freq) in band_str:
            return freq
    return None

df['Frequence'] = df['band_table'].apply(extract_frequency)

# Jointure avec les gains
df = df.merge(gain_df, how='left', on='Frequence')

# Calcul de PL
df['PL'] = df['tm_dbm'] - df['ATT_estimee'] + df['Gain'] - df['EMR_NB_PUISSANCE']

# Export CSV
df.to_csv("resultats\\resultat_PL.csv", index=False)
print("Fichier 'resultat_PL.csv' généré avec succès.")
