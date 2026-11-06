"""Tests of PEH against the geomasked drug use scenes by zone of the city, 2024 ("Jitter" columns of Appendix A).

Within each zone, the 1 km cells are clipped by the zone boundaries. A displaced scene counts in the zone where it fell;
the scenes that the displacement placed in the sea or in Guanabara Bay fall in no zone but still enter the distances.
"""
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import mannwhitneyu

from config import CRS, RESULTS, ZONES, count, duncan, grid_1km, neighborhoods, peh, scenes

MIN_POINTS_D = 5

neighborhood_polygons = neighborhoods()
zone_polygons = neighborhood_polygons.dissolve("zone").geometry.to_dict()
zones = gpd.GeoDataFrame({"zone": ZONES}, geometry=[zone_polygons[z] for z in ZONES], crs=CRS)
pieces = gpd.overlay(grid_1km()[["nome_1KM", "geometry"]], zones, how="intersection", keep_geom_type=True).reset_index(drop=True)

peh_points, scene_points = peh(2024), scenes()
j = gpd.sjoin(peh_points[["geometry"]], zones, how="left", predicate="intersects")
peh_points["zone"] = j[~j.index.duplicated()]["zone"].reindex(peh_points.index)
j = gpd.sjoin(scene_points[["geometry"]], zones, how="left", predicate="intersects")
scene_zone = j[~j.index.duplicated()]["zone"].reindex(scene_points.index)

pieces["peh_within"], pieces["peh_intersects"] = count(peh_points, pieces, "within").values, count(peh_points, pieces, "intersects").values
pieces["scenes_within"], pieces["scenes_intersects"] = count(scene_points, pieces, "within").values, count(scene_points, pieces, "intersects").values
xy = lambda d: np.column_stack([d.geometry.x, d.geometry.y])  # noqa: E731
dist = cKDTree(xy(scene_points)).query(xy(peh_points), k=1)[0]

rows = []
for zone in ZONES:
    p = pieces[pieces["zone"] == zone]
    used = p[(p["peh_within"] > 0) | (p["scenes_within"] > 0)]
    with_scene, without_scene = used[used["scenes_within"] > 0]["peh_within"], used[used["scenes_within"] == 0]["peh_within"]
    n_scenes = int((scene_zone == zone).sum())
    rows.append({
        "Zone": zone,
        "Scenes": n_scenes,
        "Median ratio (with / without)": round(with_scene.median() / without_scene.median(), 1) if without_scene.median() else np.nan,
        "Mann-Whitney p": round(mannwhitneyu(with_scene, without_scene, alternative="greater").pvalue, 3),
        "Median distance to a scene (m)": round(float(np.median(dist[(peh_points["zone"] == zone).values]))),
        "D by 1 km cell (%)": round(duncan(p["peh_intersects"], p["scenes_intersects"]), 1) if n_scenes >= MIN_POINTS_D else np.nan,
    })
results = pd.DataFrame(rows)
print(results.to_string(index=False))
results.to_csv(RESULTS / "tests_by_zone_jittered.csv", index=False)
