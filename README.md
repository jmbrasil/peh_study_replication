# Replication code: People Experiencing Homelessness in Rio de Janeiro

Code to repeat the analyses of the master's dissertation *Locations and Concentrations of People Experiencing Homelessness in Rio de Janeiro* (Joao Brasil, FGV EBAPE, 2026) with the public data.

**Data:** https://doi.org/10.5281/zenodo.23992933

The data files are under embargo; the record shows the date they open. Until then, logged-in Zenodo users can request access on the record page. The code cannot run without these files.

The dataset has the geomasked drug use scenes, not the real locations, which are not public. This code therefore repeats the tests with the displaced scenes (Appendix A of the dissertation), not the results obtained with the real locations. The case study of Chapter 4 is not covered.

Census records made by observation usually contain only age, sex and color/race (all according to the census taker's perception), plus longitude and latitude.

The censuses cover 2020, 2022 and 2024. The locations of open drug use scenes are available for 2024 only; in all three censuses, the columns `local_coleta` and `cena_de_uso` show which records were collected at a scene.

The scenes were recorded by the census teams during the 2024 PEH census, not by an independent survey. The two datasets are therefore not independent: a scene could only be recorded where the census teams went, and proximity between PEH and scenes partly reflects how the data were collected.

## How to run

1. Install the packages: `pip install -r requirements.txt`
2. Download the files from Zenodo into a folder named `data`, or set `PSR_DATA_DIR` to their folder.
3. Create the 1 km grid, which is not redistributed with the data (it downloads about 400 MB from the IBGE):

   ```
   python 01_clip_grid_1km.py
   ```

   If the link has changed, download the 1 km grid from the IBGE and use `python 01_clip_grid_1km.py --zip BR1KM.zip`.
4. Run the analyses. Results are saved in `results/`.

   ```
   python 02_tests_city.py
   python 03_tests_by_zone.py
   python 04_dissimilarity_population.py
   ```

`01_clip_grid_200m.py` clips the 200 m grid. It needs quadrant ID_26 of the IBGE grid, downloaded by hand, and is not used by the tests.

## Expected results

`02_tests_city.py` (city, jittered scenes):

| Measure | Value |
|---|---:|
| Moran's I on the 1 km grid (Rook) | 0.405 (p = 0.001) |
| Cells with a scene (without PEH) | 123 (36) |
| Cells with PEH only | 196 |
| Median PEH, with / without a scene | 10.0 / 5.0 |
| PEH in cells with a scene | 56.2% |
| Mann-Whitney U (p) | 12,468 (0.303) |
| Spearman rho | 0.09 |
| Distance to the nearest scene: Q1, median, Q3 (m) | 293, 496, 846 |
| D by 1 km cell | 66.2% |

`03_tests_by_zone.py` (zones, jittered scenes):

| Zone | Scenes | Median ratio (p) | Median distance (m) | D by 1 km cell |
|---|---:|---:|---:|---:|
| Central | 16 | 3.6 (0.062) | 491 | 60.8% |
| South | 29 | 5.3 (0.035) | 413 | 48.6% |
| North | 113 | 1.8 (0.654) | 354 | 63.6% |
| Southwest | 10 | 0.0 (0.998) | 1,974 | 93.6% |
| West | 14 | 1.2 (0.428) | 7,982 | 85.5% |

`04_dissimilarity_population.py` (PEH against the 2022 resident population):

| Census | PEH | D, neighborhood | D, 1 km cell |
|---|---:|---:|---:|
| 2020 | 7,260 | 51.8% | 70.2% |
| 2022 | 7,850 | 53.8% | 69.3% |
| 2024 | 8,195 | 53.5% | 70.0% |

## License

Code: MIT. The data have their own licenses, listed in the Zenodo record.
