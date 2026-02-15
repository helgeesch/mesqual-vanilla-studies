import pypsa

from mesqual import StudyManager, databases
from mesqual_pypsa import PyPSADataset, PyPSADatasetConfig

from studies.study_02_pypsa_eur_example.src.config import STUDY_FOLDER, StudyDatabase


def get_n(scen: str) -> pypsa.Network:
    n = pypsa.Network(STUDY_FOLDER.joinpath(f'dvc/networks/{scen}.nc'), name=str(scen))
    return n


def get_study_manager() -> StudyManager:
    _db_path = STUDY_FOLDER.joinpath(f'dvc/networks/__pickleDB')
    _db_path.mkdir(exist_ok=True)

    db = StudyDatabase(_db_path)

    study = StudyManager.factory_from_scenarios(
        scenarios=[
            PyPSADataset(
                get_n(scen), name=scen, database=db
            )
            for scen in ['base', 'high_res', 'low_res']
        ],
        comparisons=[('high_res', 'base'), ('high_res', 'base')]
    )
    return study


if __name__ == '__main__':
    study = get_study_manager()
