
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
import datashader as ds
import datashader.transfer_functions as tf
import colorcet

df_test = pd.read_csv("resultats/attenuation_estimee_testset.csv")
df_base = pd.read_csv("resultats/pci_associes_infos_corriges.csv", low_memory=False)
df_base = df_base.rename(columns={"latitude": "Latitude", "longitude": "Longitude"})
df = pd.merge(df_test, df_base, on=["Latitude", "Longitude"], how="left")
df = df.dropna(subset=["Latitude", "Longitude", "tm_dbm"])

cvs = ds.Canvas(
    plot_width=1000,
    plot_height=1000,
    x_range=(df["Longitude"].min(), df["Longitude"].max()),
    y_range=(df["Latitude"].min(), df["Latitude"].max())
)
agg = cvs.points(df, 'Longitude', 'Latitude', ds.mean('tm_dbm'))
img = tf.shade(agg, cmap=colorcet.fire, how='eq_hist')
img.to_pil().save("visualisations/graph5_heatmap_datashader_pmes.png")
