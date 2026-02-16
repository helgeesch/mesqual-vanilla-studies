import numpy as np
import pypsa

from mesqual import StudyManager, databases
from mesqual_pypsa import PyPSADataset, PyPSADatasetConfig

from studies.study_02_pypsa_eur_example.src.config import STUDY_FOLDER, StudyDatabase


def get_n(scen: str) -> pypsa.Network:
    n = pypsa.Network(STUDY_FOLDER.joinpath(f'dvc/networks/{scen}.nc'), name=str(scen))
    return n


def _perturb_low_res(n: pypsa.Network) -> pypsa.Network:
    """Perturb the low_res network so it looks distinct from high_res in visualizations.

    Applies deterministic per-bus price shifts and per-link flow scaling to produce
    visually different map and time-series outputs.
    """
    rng = np.random.default_rng(seed=42)

    # Prices: per-bus random factor (0.9–1.1) + global offset of +5 €/MWh
    if 'marginal_price' in n.buses_t:
        mp = n.buses_t['marginal_price']
        bus_factor = 0.7 + 0.6 * rng.random(mp.shape[1])
        n.buses_t['marginal_price'] = mp * bus_factor + 5

    # Link flows: per-link random factor (0.7–1.3), applied consistently to all ports
    if 'p0' in n.links_t:
        link_factor = 0.4 + 1.2 * rng.random(n.links_t['p0'].shape[1])
        for attr in ['p0', 'p1', 'p2', 'p3']:
            if attr in n.links_t and not n.links_t[attr].empty:
                n.links_t[attr] = n.links_t[attr] * link_factor

    return n


def get_study_manager() -> StudyManager:
    _db_path = STUDY_FOLDER.joinpath(f'dvc/networks/__pickleDB')
    _db_path.mkdir(exist_ok=True)

    db = StudyDatabase(_db_path)

    scenarios = []
    for scen in ['base', 'high_res', 'low_res']:
        n = get_n(scen)
        if scen == 'low_res':
            n = _perturb_low_res(n)
        scenarios.append(PyPSADataset(n, name=scen, database=db))

    study = StudyManager.factory_from_scenarios(
        scenarios=scenarios,
        comparisons=[('high_res', 'base'), ('low_res', 'base')]
    )
    return study


if __name__ == '__main__':
    study = get_study_manager()