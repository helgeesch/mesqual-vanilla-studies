from __future__ import annotations

from typing import TYPE_CHECKING
import os
import pandas as pd
import geopandas as gpd

from mesqual.typevars import FlagType, DatasetConfigType
from mesqual.utils.folium_utils import MapCountryPlotter
from mesqual.energy_data_handling.area_accounting import AreaBorderModelGenerator

from mesqual_pypsa.network_interpreters.base import PyPSAInterpreter

if TYPE_CHECKING:
    from mesqual_pypsa.pypsa_config import PyPSADatasetConfig
    from shapely import Point


class CountriesModelInterpreter(PyPSAInterpreter):
    _country_plotter = MapCountryPlotter()

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'countries'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'buses'}

    def _fetch(self, flag: FlagType, effective_config: PyPSADatasetConfig, **kwargs) -> pd.Series | pd.DataFrame:
        countries = self.parent_dataset.fetch('buses')['country'].unique().tolist()
        _country_searchable = [c.replace('NO', 'NOR') for c in countries]
        geometries = [self._country_plotter.get_geojson_for_country(c).geometry.iloc[0] for c in _country_searchable]
        return gpd.GeoDataFrame({'geometry': geometries}, index=countries, crs="EPSG:4326").rename_axis('Country')


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
        country_border_model_df = border_model_gen.generate_area_border_model()
        country_border_model_df = border_model_gen.enhance_with_geometry(country_border_model_df, country_model_df)
        return country_border_model_df


