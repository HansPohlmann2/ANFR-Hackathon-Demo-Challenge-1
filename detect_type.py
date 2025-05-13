
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
import geopandas as gpd
from shapely.geometry import Point

# 1. Charger le fichier CSV avec les coordonnées en DMS
df = pd.read_csv("ressources\\SUP_SUPPORT.csv",sep=None, engine="python")  # ← Ton fichier source

df = df.rename(columns={"LAT_DECIMAL": "LAT", "LONG_DECIMAL": "LON"})

# 3. Créer des objets géographiques
geometry = [Point(xy) for xy in zip(df["LON"], df["LAT"])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# 4. Charger le shapefile complet (avec géométrie)
communes = gpd.read_file("ressources\\corr_cont_communes_types.shp")

# S’assurer que les deux couches sont dans le même CRS
if communes.crs != "EPSG:4326":
    communes = communes.to_crs("EPSG:4326")

# 5. Jointure spatiale pour récupérer uniquement le type de milieu
result = gpd.sjoin(gdf_points, communes[["TYPE", "geometry"]], how="left", predicate="within")

# 6. Exporter uniquement les résultats utiles
final = result[["STA_NM_ANFR", "LAT", "LON", "TYPE"]]
final.to_csv("resultats\\type_de_milieu_par_point.csv", sep=";", index=False)
