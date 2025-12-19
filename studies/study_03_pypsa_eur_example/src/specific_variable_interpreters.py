import pandas as pd

from mesqual.typevars import FlagType, DatasetConfigType
from mesqual.utils.pandas_utils.pend_props import prepend_model_prop_levels

from mesqual_pypsa.network_interpreters.base import PyPSAInterpreter
from mesqual.energy_data_handling.area_accounting import AreaPriceCalculator


class BusLoads(PyPSAInterpreter):

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'buses_t.load_p'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'loads_t.p', 'loads'}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        loads = self.parent_dataset.fetch('loads')
        loads_t = self.parent_dataset.fetch('loads_t.p')
        loads_t = prepend_model_prop_levels(loads_t, loads, 'bus')
        return loads_t.T.groupby(level='bus').sum().T.rename_axis('Bus', axis=1)


class CountryVolWeightedPrice(PyPSAInterpreter):
    """Calculates Demand Volume Weighted Price per country"""
    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'countries_t.vol_weighted_marginal_price'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'buses_t.marginal_price', 'buses_t.load_p', 'buses'}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        parent_ds = self.parent_dataset

        bus_model_df = parent_ds.fetch('buses')
        prices = parent_ds.fetch('buses_t.marginal_price')
        loads = parent_ds.fetch('buses_t.load_p')

        area_price_gen = AreaPriceCalculator(node_model_df=bus_model_df, area_column='country')
        area_price = area_price_gen.calculate(node_price_df=prices, weighting_factor_df=loads)
        return area_price.rename_axis('Country', axis=1)


class BranchesP(PyPSAInterpreter):
    _object_classes_to_merge = ['lines', 'links', 'transformers']

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'branches_t.p0', 'branches_t.p1'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {f'{f}_t.p{n}' for f in self._object_classes_to_merge for n in [0, 1]}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        which_power = str(flag)[-1]
        branches_t_p = pd.concat(
            [
                self.parent_dataset.fetch(f'{f}_t.p{which_power}')
                for f in self._object_classes_to_merge
            ],
            axis=1
        ).rename_axis('Branch', axis=1)
        return branches_t_p


class CountryBorderFlows(PyPSAInterpreter):

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {
            # 'country_borders_t.p0',
            # 'country_borders_t.p1',
            'country_borders_t.net_flow',
        }

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'branches'}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        from mesqual.energy_data_handling import NetworkLineFlowsData, BorderFlowCalculator

        country_border_model_df = self.parent_dataset.fetch('country_borders')
        branch_model_df = self.parent_dataset.fetch('branches')
        bus_model_df = self.parent_dataset.fetch('buses')

        flow_calc = BorderFlowCalculator(
            country_border_model_df,
            branch_model_df,
            bus_model_df,
            'country',
            'bus0',
            'bus1',
        )
        line_flow_data = NetworkLineFlowsData.from_nodal_net_injection(
            node_a_net_injection=self.parent_dataset.fetch('branches_t.p0'),
            node_b_net_injection=self.parent_dataset.fetch('branches_t.p1'),
        )
        return flow_calc.calculate(line_flow_data, 'sent', 'net')


if __name__ == '__main__':
    from pypsa import Network
    from mesqual_pypsa import PyPSADataset
    from studies.study_03_pypsa_eur_example.src.specific_model_interpreters import (
        TransmissionModelInterpreter,
        CountriesModelInterpreter,
        CountryBordersModelInterpreter,
    )

    PyPSADataset.register_interpreter(TransmissionModelInterpreter)
    PyPSADataset.register_interpreter(CountriesModelInterpreter)
    PyPSADataset.register_interpreter(CountryBordersModelInterpreter)

    PyPSADataset.register_interpreter(BusLoads)
    PyPSADataset.register_interpreter(CountryVolWeightedPrice)
    PyPSADataset.register_interpreter(BranchesP)
    PyPSADataset.register_interpreter(CountryBorderFlows)

    n = Network('studies/study_03_pypsa_eur_example/non_versioned/resources/test2.nc')
    ds = PyPSADataset(n)

    bus_loads = ds.fetch('buses_t.load_p')
    print(bus_loads)

    vol_weighted_marginal_price = ds.fetch('countries_t.vol_weighted_marginal_price')
    print(vol_weighted_marginal_price)

    branches_p0 = ds.fetch('branches_t.p0')
    print(branches_p0)

    country_border_flows = ds.fetch('country_borders_t.net_flow')
    print(country_border_flows)