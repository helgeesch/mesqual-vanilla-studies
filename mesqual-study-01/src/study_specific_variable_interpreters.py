import pandas as pd

from mesqual.typevars import FlagType, DatasetConfigType
from mesqual.utils.pandas_utils.pend_props import prepend_model_prop_levels

from mesqual_pypsa.network_interpreters.base import PyPSAInterpreter


class ControlAreaVolWeightedPrice(PyPSAInterpreter):
    """Calculates Demand Volume Weighted Price per control_area"""
    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'control_areas_t.vol_weighted_marginal_price'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'buses_t.marginal_price', 'loads_t.p'}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        parent_ds = self.parent_dataset

        price_per_bus_ts = parent_ds.fetch('buses_t.marginal_price')
        bus_model_df = parent_ds.fetch('buses')

        load_model_df = parent_ds.fetch('loads')
        load_ts = parent_ds.fetch('loads_t.p')
        load_per_bus_ts = prepend_model_prop_levels(load_ts, load_model_df, 'bus')
        load_per_bus_ts = load_per_bus_ts.T.groupby('bus').sum().T
        load_per_control_area = prepend_model_prop_levels(load_per_bus_ts, bus_model_df, 'control_area')
        load_per_control_area = load_per_control_area.T.groupby(level='control_area').sum().T

        price_load_per_ca = price_per_bus_ts.multiply(load_per_bus_ts, fill_value=0)
        price_load_per_ca = prepend_model_prop_levels(price_load_per_ca, bus_model_df, 'control_area')
        price_load_per_ca = price_load_per_ca.T.groupby(level='control_area').sum().T

        vol_weighted_marginal_price_ts = price_load_per_ca.divide(load_per_control_area)
        return vol_weighted_marginal_price_ts


if __name__ == '__main__':
    from pypsa import Network
    from studies.study_01_intro_to_mesqual.scripts.setup_study_manager import ScigridDEDataset

    ScigridDEDataset.register_interpreter(ControlAreaVolWeightedPrice)

    n = Network('studies/study_01_intro_to_mesqual/data/networks_scigrid_de/base.nc')
    ds = ScigridDEDataset(n)
    vol_weighted_marginal_price = ds.fetch('control_areas_t.vol_weighted_marginal_price')
    print(vol_weighted_marginal_price)
