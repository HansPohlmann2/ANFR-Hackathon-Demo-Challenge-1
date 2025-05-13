

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

import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

scripts = [
    "graph1_pmes_vs_distance.py",
    "graph2_lowess.py",
    "graph3_geoplot.py",
    "graph4_freq_vs_distance.py",
    "graph5_heatmap.py"
]

def run_script(script):
    subprocess.run([sys.executable, f"{script}"], check=True)

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=5) as executor:
        list(tqdm(executor.map(run_script, scripts), total=len(scripts), desc="Génération des graphes"))
    print("Tous les graphes ont été générés.")
