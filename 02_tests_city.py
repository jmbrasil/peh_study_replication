"""City-wide tests of PEH against the geomasked drug use scenes, 2024 ("Jittered scenes" column of Appendix A).

Results with the real scene locations cannot be reproduced, because those locations are not public.
"""
import numpy as np
import pandas as pd
from esda.moran import Moran
from libpysal.weights import Rook
from scipy.spatial import cKDTree
from scipy.stats import mannwhitneyu, spearmanr

import geopandas as gpd

from config import DATA, RESULTS, CRS, count, duncan, grid_1km, neighborhoods, peh, scenes

neighborhood_polygons = neighborhoods()
peh_points, scene_points = peh(2024), scenes()
assert len(peh_points) == 8195 and len(scene_points) == 195
grid = grid_1km()
non_habitable = gpd.read_file(DATA / "non_habitable_areas_2018.gpkg").to_crs(CRS).union_all()

# Moran's I: count of scenes in the cells that touch the habitable area, without cells that have no Rook neighbor
g = grid.loc[grid.intersects(neighborhood_polygons.union_all().difference(non_habitable)), ["geometry"]].reset_index(drop=True)
g = g.drop(index=Rook.from_dataframe(g, silence_warnings=True).islands).reset_index(drop=True)
g["n"] = count(scene_points, g)
w = Rook.from_dataframe(g, silence_warnings=True)
w.transform = "r"
np.random.seed(42)
moran = Moran(g["n"], w, permutations=999)

# Quadrats: cells with PEH or with a scene
n_peh, n_scenes_cell = count(peh_points, grid), count(scene_points, grid)
used = (n_peh > 0) | (n_scenes_cell > 0)
with_scene, without_scene = n_peh[used & (n_scenes_cell > 0)], n_peh[used & (n_scenes_cell == 0)]
u, p = mannwhitneyu(with_scene, without_scene, alternative="greater")

# Distance from each person to the nearest scene
xy = lambda d: np.column_stack([d.geometry.x, d.geometry.y])  # noqa: E731
dist = cKDTree(xy(scene_points)).query(xy(peh_points), k=1)[0]
q1, median, q3 = np.percentile(dist, [25, 50, 75])

results = pd.Series({
    "Moran's I (Rook, 1 km grid)": round(moran.I, 3),
    "Moran's I: pseudo p-value": round(moran.p_sim, 3),
    "Cells with a scene": len(with_scene),
    "Cells with a scene and no PEH": int((with_scene == 0).sum()),
    "Cells with PEH only": len(without_scene),
    "Median PEH, cells with a scene": with_scene.median(),
    "Median PEH, cells without a scene": without_scene.median(),
    "PEH in cells with a scene (%)": round(100 * with_scene.sum() / n_peh.sum(), 1),
    "Mann-Whitney U": round(u),
    "Mann-Whitney p": round(p, 3),
    "Spearman rho": round(spearmanr(n_peh[used], n_scenes_cell[used])[0], 2),
    "Distance to nearest scene, Q1 (m)": round(q1),
    "Distance to nearest scene, median (m)": round(median),
    "Distance to nearest scene, Q3 (m)": round(q3),
    "D by 1 km cell (%)": round(duncan(n_peh, n_scenes_cell), 1),
}, name="Jittered scenes")
print(results.to_string())
results.to_csv(RESULTS / "tests_city_jittered.csv")
