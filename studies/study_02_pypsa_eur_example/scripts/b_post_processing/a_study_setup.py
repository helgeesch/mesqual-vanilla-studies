from pathlib import Path
import pypsa

from mesqual import StudyManager
from mesqual_pypsa import PyPSADataset, PyPSADatasetConfig

from studies.study_02_pypsa_eur_example.src.config import STUDY_FOLDER, StudyDatabase


def get_study_manager() -> StudyManager:
    db = _get_study_db()
    study = StudyManager.factory_from_scenarios(
        scenarios=[
            PyPSADataset(
                pypsa.Network(_get_network_path(scen)),
                name=scen,
                database=db,
            )
            for scen in ['base', 'high_res', 'low_res']
        ],
        comparisons=[('high_res', 'base'), ('high_res', 'base')]
    )
    return study


def _get_study_db() -> StudyDatabase:
    _db_path = STUDY_FOLDER.joinpath(f'dvc/networks/__pickleDB')
    _db_path.mkdir(exist_ok=True)
    return StudyDatabase(_db_path)


def _get_network_path(scenario_name: str) -> Path:
    return STUDY_FOLDER.joinpath(f'dvc/networks/{scenario_name}.nc')


if __name__ == '__main__':
    study = get_study_manager()
