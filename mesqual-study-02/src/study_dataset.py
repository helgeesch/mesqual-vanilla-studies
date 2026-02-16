from mesqual_pypsa import PyPSADataset

from studies.study_02_pypsa_eur_example.src.study_interpreters import (
    TransmissionModelInterpreter,
    CountriesModelInterpreter,
    CountryBordersModelInterpreter,
    BusLoads,
    CountryVolWeightedPrice,
    CountryNetPosition,
    BranchesP,
    CountryBorderFlows,
)


PyPSADataset.register_interpreter(TransmissionModelInterpreter)
PyPSADataset.register_interpreter(CountriesModelInterpreter)
PyPSADataset.register_interpreter(CountryBordersModelInterpreter)
PyPSADataset.register_interpreter(BusLoads)
PyPSADataset.register_interpreter(CountryVolWeightedPrice)
PyPSADataset.register_interpreter(CountryNetPosition)
PyPSADataset.register_interpreter(BranchesP)
PyPSADataset.register_interpreter(CountryBorderFlows)
