"""Duncan's D of PEH with respect to the 2022 resident population, by neighborhood and by 1 km cell, in the three censuses."""
import pandas as pd

from config import DATA, RESULTS, count, duncan, grid_1km, neighborhoods, peh

neighborhood_polygons = neighborhoods()
pop = pd.read_csv(DATA / "populacao_bairros_2022.csv").set_index("codbnum")["pop_2022"]
neighborhood_polygons["pop"] = neighborhood_polygons["codbnum"].astype(int).map(pop).fillna(0)
grid = grid_1km()
grid["pop"] = grid["TOTAL"] * grid["frac_no_municipio"]

rows = []
for year in [2020, 2022, 2024]:
    peh_points = peh(year)
    by_neighborhood, by_cell = count(peh_points, neighborhood_polygons, "intersects"), count(peh_points, grid, "intersects")
    rows.append({"Census": year, "PEH": int(by_neighborhood.sum()),
                 "D, neighborhood (%)": round(duncan(by_neighborhood, neighborhood_polygons["pop"]), 1),
                 "D, 1 km cell (%)": round(duncan(by_cell, grid["pop"]), 1)})
results = pd.DataFrame(rows)
print(results.to_string(index=False))
results.to_csv(RESULTS / "dissimilarity_population.csv", index=False)
