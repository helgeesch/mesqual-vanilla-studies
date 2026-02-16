from __future__ import annotations

from typing import TYPE_CHECKING
import pandas as pd
import geopandas as gpd

from mesqual.energy_data_handling import FlowType
from mesqual.utils.pandas_utils import filter_by_model_query
from mesqual.utils.pandas_utils.pend_props import prepend_model_prop_levels
from mesqual.energy_data_handling.area_accounting import AreaPriceCalculator
from mesqual.typevars import FlagType, DatasetConfigType
from mesqual.utils.folium_utils import MapCountryPlotter
from mesqual.energy_data_handling.area_accounting import AreaBorderModelGenerator, AreaBorderGeometryCalculator

from mesqual_pypsa.network_interpreters.base import PyPSAInterpreter


if TYPE_CHECKING:
    from mesqual_pypsa.pypsa_config import PyPSADatasetConfig


class CountriesModelInterpreter(PyPSAInterpreter):
    _country_plotter = MapCountryPlotter()

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'countries'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'buses'}

    def _fetch(self, flag: FlagType, effective_config: PyPSADatasetConfig, **kwargs) -> pd.DataFrame:

        buses = self.parent_dataset.fetch('buses')
        filtered_buses = buses[buses['unit'] == 'MWh_el']

        countries = filtered_buses['country'].unique().tolist()
        geometries = [self._country_plotter.get_geojson_for_country(c).geometry.iloc[0] for c in countries]
        gdf = gpd.GeoDataFrame({'geometry': geometries}, index=countries, crs="EPSG:4326").rename_axis('Country')

        def get_largest_polygon_rep_point(geom):
            """Get representative point of the largest polygon in a geometry."""
            if geom.geom_type == 'MultiPolygon':
                largest = max(geom.geoms, key=lambda p: p.area)
            else:
                largest = geom
            return largest.representative_point()

        gdf['projection_point'] = gdf.geometry.apply(get_largest_polygon_rep_point)

        return gdf


class TransmissionModelInterpreter(PyPSAInterpreter):

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'branches'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'lines', 'links', 'transformers'}

    def _fetch(self, flag: FlagType, effective_config: PyPSADatasetConfig, **kwargs) -> pd.Series | pd.DataFrame:
        lines = self.parent_dataset.fetch('lines')
        links = self.parent_dataset.fetch('links')
        trafos = self.parent_dataset.fetch('transformers')

        branches_model_df = pd.concat([lines, links, trafos]).rename_axis('Branch')
        if any(branches_model_df.index.duplicated()):
            raise ValueError(f'Overlapping names between lines, links, and trafos. Not supported')

        branches_model_df = branches_model_df[branches_model_df['carrier'].isin(['AC', 'DC'])]
        return branches_model_df


class CountryBordersModelInterpreter(PyPSAInterpreter):

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'country_borders'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'country', 'branches'}

    def _fetch(self, flag: FlagType, effective_config: PyPSADatasetConfig, **kwargs) -> pd.Series | pd.DataFrame:
        node_model_df = self.parent_dataset.fetch('buses')
        branch_model_df = self.parent_dataset.fetch('branches')
        country_model_df = self.parent_dataset.fetch('countries')
        border_model_gen = AreaBorderModelGenerator(
            node_model_df,
            branch_model_df,
            area_column='country',
            node_from_col='bus0',
            node_to_col='bus1',
            border_identifier='_border',
            source_area_identifier='0',
            target_area_identifier='1',
        )
        border_geo_calc = AreaBorderGeometryCalculator(country_model_df)
        country_border_model_df = border_model_gen.generate_area_border_model()
        country_border_model_df = border_model_gen.enhance_with_geometry(country_border_model_df, border_geo_calc)
        return country_border_model_df


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
        electricity_buses = bus_model_df[bus_model_df['unit'] == 'MWh_el']

        prices = parent_ds.fetch('buses_t.marginal_price')
        loads = parent_ds.fetch('buses_t.load_p')

        my_buses = list(set(electricity_buses.index).intersection(prices.columns).intersection(loads.columns))
        prices = prices[my_buses]
        loads = loads[my_buses]

        area_price_gen = AreaPriceCalculator(node_model_df=electricity_buses, area_column='country')
        area_price = area_price_gen.calculate(node_price_df=prices, weighting_factor_df=loads)
        return area_price.rename_axis('Country', axis=1)


class CountryNetPosition(PyPSAInterpreter):
    """Calculates Net-Position and Trade-Balance per country"""

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'countries_t.net_position', 'countries_t.trade_balance_per_partner'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'branches', 'branches_t.p0', 'branches_t.p1'}

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        from mesqual.energy_data_handling import NetworkLineFlowsData, RegionalTradeBalanceCalculator

        branch_model_df = self.parent_dataset.fetch('branches', effective_config)
        bus_model_df = self.parent_dataset.fetch('buses', effective_config)

        trade_bal_calc = RegionalTradeBalanceCalculator(
            branch_model_df,
            bus_model_df,
            agg_region_column='country',
            node_from_col='bus0',
            node_to_col='bus1',
        )
        line_flow_data = NetworkLineFlowsData.from_nodal_net_injection(
            node_a_net_injection=self.parent_dataset.fetch('branches_t.p0', effective_config),
            node_b_net_injection=self.parent_dataset.fetch('branches_t.p1', effective_config),
        )
        trade_bal_df = trade_bal_calc.get_trade_balance(line_flow_data, flow_type=FlowType.PRE_LOSS)
        trade_bal_df.columns.name = 'Country'

        if 'trade_balance_per_partner' in flag:
            return trade_bal_df

        elif 'net_position' in flag:
            net_position = trade_bal_calc.get_net_position_per_primary_level(trade_bal_df)
            return net_position

        raise NotImplementedError(f'Flag {flag} logic not implemented in this class. check your logic.')


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
            'country_borders_t.net_flow',
        }

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'branches', 'branches_t.p0', 'branches_t.p1'}

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
