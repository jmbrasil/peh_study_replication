"""Clip the IBGE 200 m Statistical Grid (2022 Census) to the city of Rio de Janeiro.

The 200 m grid has no direct link here: download quadrant ID_26 from the IBGE and pass its shapefile. The tests in this
repository use only the 1 km grid.

Usage: python 01_clip_grid_200m.py path/to/grade_id26.shp
"""
import argparse
from pathlib import Path

import geopandas as gpd

from config import DATA, GRID


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shapefile", type=Path, help="IBGE grid quadrant ID_26 (grade_id26.shp)")
    args = parser.parse_args()
    city = gpd.read_file(DATA / "Limite_de_Bairros.shp").to_crs("EPSG:4674").union_all()
    grid = gpd.read_file(args.shapefile, bbox=city.bounds)
    grid = grid.iloc[sorted(grid.sindex.query(city, predicate="intersects"))].reset_index(drop=True)
    grid["dimensao"] = grid["ID_UNICO"].str.startswith("200M").map({True: "200m", False: "1km"})
    grid_m = grid.to_crs("EPSG:31983")
    city_m = gpd.GeoSeries([city], crs="EPSG:4674").to_crs("EPSG:31983").iloc[0]
    grid["frac_no_municipio"] = (grid_m.intersection(city_m).area / grid_m.area).round(4)
    GRID.mkdir(exist_ok=True)
    out = GRID / "grade_ibge_200m_2022_rio.gpkg"
    grid.to_file(out, layer="grade_200m", driver="GPKG")
    print(f"{len(grid):,} cells saved in {out}")


if __name__ == "__main__":
    main()
