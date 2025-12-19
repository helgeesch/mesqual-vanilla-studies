import pypsa

from mesqual import StudyManager
from mesqual_pypsa import PyPSADataset

# PyPSADataset.register_interpreter()


def get_n(scenario: str) -> pypsa.Network:
    n = pypsa.Network(f'studies/study_03_pypsa_eur_example/non_versioned/resources/test2.nc', name=scenario)
    n.set_snapshots(n.snapshots[:300])
    return n

def get_study_manager() -> StudyManager:
    study = StudyManager.factory_from_scenarios(
        scenarios=[
            PyPSADataset(
                get_n(scen), name=scen
            )
            for scen in ['base', 'high_res', 'cheap_gas']
        ],
        comparisons=[('high_res', 'base'), ('cheap_gas', 'base')]
    )
    return study


if __name__ == '__main__':
    study = get_study_manager()