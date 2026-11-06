"""Download the IBGE 1 km Statistical Grid (2022 Census) and clip it to the city of Rio de Janeiro.

The grid is not redistributed with the data. If the link below stops working, look for grade_1km in
https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/censo_2022/ and use --zip.

Usage: python 01_clip_grid_1km.py [--zip BR1KM.zip]
"""
import argparse
import tempfile
import urllib.request
from pathlib import Path

import geopandas as gpd
import pyogrio

from config import DATA, GRID

URL = ("https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/"
       "censo_2022/grade_1km/BR1KM_20251002.zip")


def clip(zip_path):
    city = gpd.read_file(DATA / "neighborhood_boundaries.gpkg").to_crs("EPSG:4674").union_all()
    grid = pyogrio.read_dataframe(f"/vsizip/{zip_path}/BR1KM.shp", bbox=city.bounds)
    grid = grid[grid.intersects(city)].reset_index(drop=True)
    grid_m = grid.to_crs("EPSG:31983")
    city_m = gpd.GeoSeries([city], crs="EPSG:4674").to_crs("EPSG:31983").iloc[0]
    grid["frac_no_municipio"] = (grid_m.intersection(city_m).area / grid_m.area).round(4)
    return grid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, help="BR1KM zip already downloaded")
    args = parser.parse_args()
    if args.zip:
        grid = clip(args.zip.resolve())
    else:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "BR1KM.zip"
            print(f"Downloading {URL} (about 400 MB)...")
            urllib.request.urlretrieve(URL, zip_path)
            grid = clip(zip_path)
    GRID.mkdir(exist_ok=True)
    out = GRID / "grade_ibge_1km_2022_rio.gpkg"
    grid.to_file(out, layer="grade_1km", driver="GPKG")
    print(f"{len(grid):,} cells saved in {out}")


if __name__ == "__main__":
    main()
