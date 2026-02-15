# study_interpreters.py

[:octicons-mark-github-16: View on GitHub](https://github.com/helgeesch/mesqual-vanilla-studies/blob/main/studies/study_02_pypsa_eur_example/src/study_interpreters.py){ .md-button }

Custom interpreters that extend `PyPSADataset` with derived data specific to this study:

- **CountriesModelInterpreter** — builds a country-level GeoDataFrame from bus topology
- **TransmissionModelInterpreter** — aggregates lines, links, and transformers into a unified branches model
- **CountryBordersModelInterpreter** — detects cross-border connections and computes border geometries
- **BusLoads** — aggregates load time series to the bus level
- **CountryVolWeightedPrice** — calculates demand volume-weighted marginal prices per country
- **CountryNetPosition** — computes net positions and bilateral trade balances between countries
- **BranchesP** — merges power flow time series (p0, p1) across all branch types
- **CountryBorderFlows** — calculates net cross-border electricity flows

```python
--8<-- "studies/study_02_pypsa_eur_example/src/study_interpreters.py"
```
