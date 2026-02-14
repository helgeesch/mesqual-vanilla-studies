# Study 04 — PyPSA-Eur Example

This study demonstrates a typical MESQUAL workflow using three PyPSA-Eur network scenarios (`base`, `high_res`, `low_res`). It serves as a reference for how studies are structured in practice.

## How a Study is Organized

### `src/` — Study-Specific Extensions

All custom logic lives here. This is where you extend the generic MESQUAL framework with study-specific interpreters, flags, and configuration.

| File | Purpose                                                                                                                  |
|------|--------------------------------------------------------------------------------------------------------------------------|
| `study_interpreters.py` | Custom interpreters that add new flags (e.g. country models from bus topology, border detection, volume-weighted prices) |
| `study_dataset.py` | Registers all custom interpreters on `PyPSADataset` so they're available via `.fetch()`                                  |
| `study_database.py` | Study-specific caching strategy (only caches custom flags, not raw PyPSA data)                                           |
| `config.py` | Central imports, `STUDY_FOLDER` path, and theme setup — every script usually imports from here                           |

### `scripts/` — Analysis Pipeline

Scripts are prefixed alphabetically to define execution order. The simplest way to work with them is in a **Python console with a persistent workspace** (e.g. PyCharm's Python Console) — variables from earlier scripts stay in memory, so you build up state interactively.

The typical workflow:

1. **Run `a_study_setup.py` once** — creates the `StudyManager` with all scenarios and comparisons. The `study` variable stays in your console's namespace.
2. **Run any subsequent script** — each one uses the existing `study` instance to perform a self-contained analysis or visualization.

| Script | What it does |
|--------|-------------|
| `a_study_setup.py` | Creates the `StudyManager` with 3 PyPSA scenarios and their comparisons |
| `b_simple_fetch.py` | Demonstrates the `.fetch()` interface — scenarios, comparisons, and combined access |
| `c_trade_balance_heatmap_dashboard.py` | Builds a faceted heatmap dashboard of cross-border trade balances |
| `c_trade_balance_line_fig.py` | Creates an interactive line chart of net-positions over time |
| `d_netpos_price_map.py` | Generates a multi-layer Folium map with KPI-colored areas and animated flow arrows |

Each script is independent — you can run them in any order after the setup script. Each one typically produces an output (DataFrame, Plotly figure, HTML dashboard, or Folium map).

### `dvc/` — Generated Data (gitignored)

- `dvc/networks/` — PyPSA network files (`base.nc`, `high_res.nc`, `low_res.nc`)
- `dvc/output/` — Exported results, figures, and HTML dashboards
