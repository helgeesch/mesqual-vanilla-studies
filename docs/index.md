# <img src="https://raw.githubusercontent.com/helgeesch/mesqual/18fe3fc20bace115a116555b2872d57925698e48/assets/logo-turq.svg" width="30" height="30" alt="MESQUAL logo"> Welcome to MESQUAL Suite Documentation

**MESQUAL** (**M**odular **E**nergy **S**cenario Comparison Library for **Qu**antitative and **Qu**alitative An**al**ysis) is a platform-agnostic Python framework for multi-scenario energy systems analysis.

## What is MESQUAL?

MESQUAL provides a unified data access layer, automatic scenario comparison, and comprehensive visualization capabilities that work seamlessly across any energy modeling platform (PyPSA, PLEXOS, SimFa, etc.) or custom data sources.

### Core Philosophy

MESQUAL follows a three-tier code organization principle:

- **General code** (mesqual): Platform-agnostic framework available in all studies
- **Platform-specific code** (mesqual-pypsa, mesqual-plexos, etc.): Platform interfaces and interpreters
- **Study-specific code** (your-study-repo): Custom variables, analysis logic, and workflows

## Quick Navigation

### 📚 Learn About MESQUAL

- **[MESQUAL Framework](about_mesqual.md)** - Comprehensive overview of the core framework, architecture, and capabilities
- **[Vanilla Studies Repository](about_vanilla_studies.md)** - Template architecture for organizing energy modeling studies

### 🔍 Explore the API

- **[MESQUAL API Reference](mesqual-package-documentation/api_reference/study_manager/)** - Complete API documentation for the core package
  - [StudyManager](mesqual-package-documentation/api_reference/study_manager/) - Central orchestrator for multi-scenario analysis
  - [Datasets](mesqual-package-documentation/api_reference/datasets/) - Platform-agnostic data access layer
  - [KPI System](mesqual-package-documentation/api_reference/kpis/) - Advanced KPI framework with model object integration
  - [Visualization Modules](mesqual-package-documentation/api_reference/visualization/) - Folium maps, Plotly dashboards, and HTML reports
  - [Energy Data Handling](mesqual-package-documentation/api_reference/energy_data_handling/) - Area accounting, network flows, and more

### 🎓 Hands-On Examples

- **[Intro to MESQUAL](mesqual-study-01//)** - Comprehensive tutorial series covering:
  - Data fetching and scenario comparison
  - KPI calculation and analysis
  - Interactive Folium map visualization
  - Custom interpreter development

## Key Features

**🎯 Unified Data Access**
- Single `.fetch(flag)` interface across all platforms
- Consistent API for model data, time series, and computed metrics
- Automatic MultiIndex handling for multi-scenario analysis

**📊 Multi-Scenario Management**
- Three-tier collection system (`.scen`, `.comp`, `.scen_comp`)
- Automatic delta computation between scenarios
- Unified access with type distinction

**🗺️ Rich Visualization System**
- Interactive Folium maps with automatic feature generation
- PropertyMapper system for data-driven styling
- Time series dashboards and HTML reports

**⚡ Energy-Specific Tools**
- Area-level accounting for topological aggregation
- Network flow analysis and capacity modeling
- Volume-weighted price aggregation
- Time series granularity conversion

## Getting Started

### Installation

Install the core framework from Git:
```bash
pip install git+https://github.com/helgeesch/mesqual.git
```

Or for local development with the vanilla-studies (or your-own-studies) repository:
```bash
git clone https://github.com/helgeesch/mesqual-vanilla-studies.git
cd mesqual-vanilla-studies
git submodule update --init
pip install -e ./submodules/mesqual
pip install -e ./submodules/mesqual-pypsa
pip install -r requirements.txt
```

### Quick Example

```python
import pypsa
from mesqual import StudyManager
from mesqual_pypsa import PyPSADataset

# Load networks
n_base = pypsa.Network('your_base_network.nc')
n_scen1 = pypsa.Network('your_scen1_network.nc')

# Initialize study manager
study = StudyManager.factory_from_scenarios(
    scenarios=[
        PyPSADataset(n_base, name='base'),
        PyPSADataset(n_scen1, name='scen1'),
    ],
    comparisons=[("scen1", "base")],
    export_folder="output"
)

# Access MultiIndex df with data for all scenarios
df_prices = study.scen.fetch("buses_t.marginal_price")

# Access comparison deltas
df_price_deltas = study.comp.fetch("buses_t.marginal_price")
```

## Repository Structure

This documentation covers the entire MESQUAL suite:

```
mesqual/                         # Core framework (submodule)
mesqual-pypsa/                   # PyPSA interface (submodule)
mesqual-vanilla-studies/         # This repository
├── vanilla/                     # Generic utilities reused across all studies
├── studies/                     # Individual study folders
│   └── study_01_intro_to_mesqual/  # Comprehensive tutorial
├── submodules/                  # Independent packages
└── docs/                        # This documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

- [MESQUAL Core Repository](https://github.com/helgeesch/mesqual)
- [Vanilla Studies Repository](https://github.com/helgeesch/mesqual-vanilla-studies)
- [PyPSA Interface](https://github.com/helgeesch/mesqual-pypsa)

## License

MESQUAL is licensed under the LGPL License - see the LICENSE file for details.

## Contact

For questions or feedback, don't hesitate to get in touch!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/helge-e-8201041a7/)