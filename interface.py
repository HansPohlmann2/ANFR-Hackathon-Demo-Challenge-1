
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

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg="#f4f4f4")
        self.option_add("*Font", "Arial 11")
        self.title("Estimation de l'atténuation de la propagation électromagnétique")
        self.geometry("700x300")  # un peu plus haut pour inclure le bouton

        # Titre principal
        tk.Label(self,
                 text="Estimation de l'atténuation de la propagation électromagnétique",
                 font=("Arial", 20, "bold"),
                 fg="black", bg="#f4f4f4", wraplength=680, justify="center").pack(pady=(30, 10))

        # Label de statut
        self.label_status = tk.Label(self, text="Initialisation...",
                                     fg="blue", bg="#f4f4f4",
                                     font=("Arial", 12))
        self.label_status.pack(pady=10)

        # Barre de progression
        self.progress = ttk.Progressbar(self, mode='determinate', length=500)
        self.progress.pack(pady=10)

        # Bouton pour lancer la visualisation (masqué au départ)
        self.bouton_visualisation = ttk.Button(self,
            text="Lancer la visualisation",
            command=self.lancer_visualisation)
        self.bouton_visualisation.pack(pady=10)
        self.bouton_visualisation.pack_forget()  # cacher par défaut

        self.bouton_calcul_pl = ttk.Button(
            self,
            text="Calculer PL",
            command=self.calculer_pl

        )
        self.bouton_visualisation.pack(pady=10)
        self.bouton_visualisation.pack_forget()  # cacher par défaut
        # Crédits
        tk.Label(self,
                 text="Projet réalisé par Mathieu Witkowski - Clément Poucet - Hans Pohlmann",
                 font=("Arial", 10), fg="blue", bg="#f4f4f4").pack(side="bottom", pady=10)

        # Lancement en tâche de fond
        threading.Thread(target=self.lancer_pipeline).start()

    def calculer_pl(self):
        try:
            subprocess.run(["python", "resultatsPL.py"],
                           check=True)
            self.verifier_pl()
            subprocess.run(["python","visualisation_pl.py"],
                           check=True)
        except Exception as e:
            self.label_status.config(text=f"Erreur calcul PL : {e}")


    def verifier_pl(self):
        fichier = [
            "resultats\\resultat_PL.csv"
        ]

        manquants = [f for f in fichier if not os.path.exists(f)]
        if not manquants:
            self.label_status.config(
                text="Toutes les valeurs de PL calculées avec succès.")

    def update_status(self, message, progress=None):
        self.label_status.config(text=message)
        if progress is not None:
            self.progress.config(value=progress)
        self.update_idletasks()

    def lancer_pipeline(self):
        try:
            if not os.path.exists("resultats\\type_de_milieu_par_point.csv"):
                self.update_status("Traitement des types de milieux en cours...", 10)
                subprocess.run(["python", "detect_type.py"], check=True)
            else:
                self.update_status("Types de milieux déjà traités.", 10)

            if not os.path.exists("resultats\\pci_associes_infos_corriges.csv"):
                self.update_status("Traitement des mesures en cours...", 40)
                subprocess.run(["python", "testPolars.py"], check=True)
            else:
                self.update_status("Données de mesure déjà disponibles.", 40)

            if not os.path.exists("resultats\\random_forest_att_model.pkl"):
                self.update_status("Entraînement du modèle de prédiction...", 70)
                subprocess.run(["python", "trainRandomForest.py"], check=True)
            else:
                self.update_status("Modèle de prédiction déjà entraîné.", 70)

            self.update_status("Toutes les données sont prêtes !", 100)

            # Afficher le bouton de visualisation
            self.bouton_visualisation.pack()
            self.bouton_calcul_pl.pack()

        except subprocess.CalledProcessError as e:
            self.update_status(f"Erreur lors de l'exécution : {e}")
        except Exception as e:
            self.update_status(f"Erreur inattendue : {e}")

    # Lancer visualisation via subprocess
    def lancer_visualisation(self):
        try:
            subprocess.run(["python", "generate_all_graphs.py"],
                           check=True)
            self.verifier_graphs()
        except Exception as e:
            self.label_status.config(text=f"Erreur visualisation : {e}")

    def verifier_graphs(self):
        fichiers = [
            "visualisations\\graph1_pmes_vs_distance.png",
            "visualisations\\graph2_lowess_pmes_vs_distance.png",
            "visualisations\\graph3_carte_geographique_pmes.png",
            "visualisations\\graph4_distance_vs_frequence.png",
            "visualisations\\graph5_heatmap_datashader_pmes.png"
        ]

        manquants = [f for f in fichiers if not os.path.exists(f)]
        if manquants:
            self.label_status.config(
                text=f"Graphes manquants : {', '.join(os.path.basename(f) for f in manquants)}")
        else:
            self.label_status.config(
                text="Tous les graphes ont été générés avec succès.")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
