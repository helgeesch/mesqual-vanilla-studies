from typing import TYPE_CHECKING
import os
import pandas as pd
import geopandas as gpd

from mesqual.typevars import FlagType, DatasetConfigType
from mesqual_pypsa.network_interpreters.base import PyPSAInterpreter
from mesqual_pypsa.network_interpreters.model import PyPSAModelInterpreter

if TYPE_CHECKING:
    from mesqual_pypsa.pypsa_config import PyPSADatasetConfig
    from shapely import Point


_PATH_TO_GEOJSON = os.path.join('studies/study_01_intro_to_mesqual/data/DE_control_areas.geojson')


def _get_control_area_gdf() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(_PATH_TO_GEOJSON)
    gdf = gdf.rename(columns={'tso': 'control_area'})
    gdf = gdf.set_index('control_area')
    gdf = gdf.set_crs(epsg=4326)
    return gdf


class ControlAreaModelInterpreter(PyPSAInterpreter):
    GDF = _get_control_area_gdf()

    @property
    def accepted_flags(self) -> set[FlagType]:
        return {'control_areas'}

    def _required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return set()

    def _fetch(self, flag: FlagType, effective_config: DatasetConfigType, **kwargs) -> pd.Series | pd.DataFrame:
        # Due to the @flag_must_be_accepted decorator in the self.fetch method,
        # we can be sure that the flag is 'control_areas' at this point.
        # --> So no further flag logic is needed at this point.
        return self.GDF


class ScigridDEBusModelInterpreter(PyPSAModelInterpreter):
    @property
    def accepted_flags(self) -> set[str]:
        return {'buses'}

    def required_flags_for_flag(self, flag: FlagType) -> set[FlagType]:
        return {'control_areas'}

    def _fetch(self, flag: str, effective_config: 'PyPSADatasetConfig', **kwargs) -> pd.Series | pd.DataFrame:
        df_buses = super()._fetch(flag, effective_config, **kwargs)

        # The instance (self) will have the PyPSADataset instance as it's parent_dataset, so we can fetch from there
        df_control_areas = self.parent_dataset.fetch('control_areas')

        df_buses = gpd.GeoDataFrame(df_buses, geometry='location', crs='EPSG:4326')
        sjoined = gpd.sjoin(df_buses, df_control_areas.reset_index(), how='left', predicate='within')
        df_buses['control_area'] = sjoined['control_area']

        missing_mask = df_buses['control_area'].isna()
        if missing_mask.any():
            projected_crs = 'EPSG:3857'
            df_buses_proj = df_buses.to_crs(projected_crs)
            df_control_area_proj = df_control_areas.to_crs(projected_crs)

            def find_nearest_control_area(bus):
                return df_control_area_proj.geometry.distance(bus.location).idxmin()

            _missing_areas = df_buses_proj.loc[missing_mask].apply(find_nearest_control_area, axis=1)
            df_buses.loc[missing_mask, 'control_area'] = _missing_areas

        return df_buses
