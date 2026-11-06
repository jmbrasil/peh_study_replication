"""Paths and shared helpers. Set PSR_DATA_DIR to the folder with the files downloaded from Zenodo."""
import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("PSR_DATA_DIR", ROOT / "data"))
GRID = Path(os.environ.get("PSR_GRID_DIR", ROOT / "grid"))
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
CRS = "EPSG:31983"
ZONES = ["Central", "South", "North", "Southwest", "West"]
ZONE_OF_AP = {"1": "Central", "3": "North", "4": "Southwest", "5": "West"}
ZONE_OF_RP_AP2 = {"2.1": "South", "2.2": "North"}


def neighborhoods():
    """The 166 neighborhoods, with the zone of each one (Planning Areas and Planning Regions, no exceptions)."""
    b = gpd.read_file(DATA / "limite_de_bairros.gpkg").to_crs(CRS).reset_index(drop=True)
    ap = b["area_plane"].astype(str).str.strip()
    rp = b["cod_rp"].astype(str).str.strip()
    zone = ap.map(ZONE_OF_AP)
    zone[ap.eq("2")] = rp[ap.eq("2")].map(ZONE_OF_RP_AP2)
    assert zone.notna().all()
    b["zone"] = zone
    return b


def peh(year):
    """PEH records of one census as points."""
    d = pd.read_csv(DATA / "base_harmonizada_psr_2020_2024.csv", usecols=["ano_censo", "latitude", "longitude"])
    d = d[d["ano_censo"] == year].dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    return gpd.GeoDataFrame(geometry=gpd.points_from_xy(d["longitude"], d["latitude"]), crs="EPSG:4326").to_crs(CRS)


def scenes():
    """The 195 geomasked open drug use scenes. The real locations are not public."""
    return gpd.read_file(DATA / "cenas_geomasked_2024.gpkg")[["geometry"]].to_crs(CRS)


def grid_1km():
    """IBGE 1 km grid clipped to the city, created by 01_clip_grid_1km.py."""
    path = GRID / "grade_ibge_1km_2022_rio.gpkg"
    if not path.exists():
        raise SystemExit(f"{path} not found: run 01_clip_grid_1km.py first.")
    return gpd.read_file(path, layer="grade_1km").to_crs(CRS).reset_index(drop=True)


def count(points, units, predicate="within"):
    """Points in each unit; a point on the border between two units counts once."""
    j = gpd.sjoin(points[["geometry"]], units[["geometry"]], how="inner", predicate=predicate)
    j = j[~j.index.duplicated()]
    return j.groupby("index_right").size().reindex(units.index).fillna(0)


def duncan(a, b):
    """Duncan's dissimilarity index, from 0 to 100."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return 50 * np.abs(a / a.sum() - b / b.sum()).sum()
