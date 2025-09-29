import os
import glob
import pypsa

from mesqual import StudyManager
from mesqual_pypsa import PyPSADataset

from studies.study_01_intro_to_mesqual.src.study_specific_model_interpreters import ControlAreaModelInterpreter, ScigridDEBusModelInterpreter
from studies.study_01_intro_to_mesqual.src.study_specific_variable_interpreters import ControlAreaVolWeightedPrice


class ScigridDEDataset(PyPSADataset):
    @classmethod
    def _register_core_interpreters(cls):
        cls.register_interpreter(ControlAreaModelInterpreter)
        cls.register_interpreter(ScigridDEBusModelInterpreter)
        cls.register_interpreter(ControlAreaVolWeightedPrice)


ScigridDEDataset._register_core_interpreters()


def _get_name_from_path(file_path: str) -> str:
    return os.path.basename(file_path).replace('.nc', '')


def _get_attributes_from_name(model_name: str) -> dict[str, str | int]:
    attributes = dict()
    if '_' in model_name:
        res_tech, scaling_factor = model_name.split('_')
        attributes['res_tech'] = res_tech
        attributes['scaling_factor'] = scaling_factor
    return attributes


def _get_dataset_from_nc_file_path(file_path: str) -> PyPSADataset:
    name = _get_name_from_path(file_path)
    attributes = _get_attributes_from_name(name)
    n = pypsa.Network(file_path)
    return ScigridDEDataset(n, name=name, attributes=attributes)


def get_scigrid_de_study_manager() -> StudyManager:
    study_folder = 'studies/study_01_intro_to_mesqual'
    networks_folder = os.path.join(study_folder, 'data/networks_scigrid_de')
    network_files = sorted(glob.glob(os.path.join(networks_folder, '*.nc')))

    study_manager = StudyManager.factory_from_scenarios(
        scenarios=[
            _get_dataset_from_nc_file_path(f)
            for f in network_files
        ],
        comparisons=[(_get_name_from_path(f), 'base') for f in network_files if not f.endswith('base.nc')],
        export_folder=os.path.join(study_folder, 'non_versioned/output'),
    )
    return study_manager


if __name__ == '__main__':
    study = get_scigrid_de_study_manager()
