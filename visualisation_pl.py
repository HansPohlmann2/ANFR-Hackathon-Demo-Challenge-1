import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Chargement des données
df = pd.read_csv("resultats\\resultat_PL.csv")
milieu_df = pd.read_csv("resultats\\type_de_milieu_par_point.csv", sep=";")
df.columns = df.columns.str.strip()
milieu_df.columns = milieu_df.columns.str.strip()
df = df.merge(milieu_df[['STA_NM_ANFR', 'TYPE']], on='STA_NM_ANFR', how='left')

# Nettoyage des fréquences et filtrage
df['Frequence'] = pd.to_numeric(df['Frequence'], errors='coerce')
df = df.dropna(subset=['Frequence', 'TYPE'])
df = df[(df['Frequence'] < 3000) & (df['distance_to_support_km'] < 25)]
df['Frequence'] = df['Frequence'].round(0).astype(int)

# Liste cible
frequences_cible = [700, 800, 900, 1800, 2100, 2600]
df = df[df['Frequence'].isin(frequences_cible)]

# Moyenne de PL par couple (Frequence, Type)
agg = df.groupby(['Frequence', 'TYPE'])['PL'].mean().reset_index()

# Séparer en 2 groupes pour affichage
group1 = [700, 800, 900]
group2 = [1800, 2100, 2600]

pivot1 = agg[agg['Frequence'].isin(group1)].pivot(index='Frequence', columns='TYPE', values='PL')
pivot2 = agg[agg['Frequence'].isin(group2)].pivot(index='Frequence', columns='TYPE', values='PL')

# Affichage
fig, axes = plt.subplots(2, 1, figsize=(10, 10))

sns.heatmap(pivot1, annot=True, fmt=".1f", cmap='YlOrRd', ax=axes[0])
axes[0].set_title("PL moyenne : fréquences 700-900 MHz")
axes[0].set_xlabel("Type de milieu")
axes[0].set_ylabel("Fréquence (MHz)")

sns.heatmap(pivot2, annot=True, fmt=".1f", cmap='YlOrRd', ax=axes[1])
axes[1].set_title("PL moyenne : fréquences 1800-2600 MHz")
axes[1].set_xlabel("Type de milieu")
axes[1].set_ylabel("Fréquence (MHz)")

plt.tight_layout()
plt.savefig("visualisations\\heatmap_PL_frequences_en_deux_parties.png", dpi=300)
plt.show()
