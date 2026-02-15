import os
from typing import List
import numpy as np
import folium

from mesqual import StudyManager, kpis
from mesqual.kpis import KPI, KPICollection
from mesqual.visualizations import folviz, valmap
from mesqual.utils.folium_utils import set_background_color_of_map, MapCountryPlotter
from mesqual.visualizations.folium_viz_system import PropertyMapper

from studies.study_02_pypsa_eur_example.src.config import STUDY_FOLDER, theme


class KPISetup:
    """Sets up KPI definitions for prices, net positions, and flows."""

    def __init__(self, study: StudyManager):
        self._study = study

    def run(self) -> None:
        """Execute KPI setup: clear existing KPIs and add new definitions."""
        self._clear_existing_kpis()

        country_kpi_defs = self._create_country_kpi_definitions()
        flow_kpi_defs = self._create_flow_kpi_definitions()

        all_kpi_defs = country_kpi_defs + flow_kpi_defs
        self._add_kpis_to_study(all_kpi_defs)

    def _clear_existing_kpis(self) -> None:
        self._study.scen.clear_kpi_collection_for_all_child_datasets()
        self._study.comp.clear_kpi_collection_for_all_child_datasets()

    def _create_country_kpi_definitions(self) -> list:
        flags = [
            'countries_t.vol_weighted_marginal_price',
            'countries_t.net_position',
        ]
        return (
            kpis.FlagAggKPIBuilder()
            .for_flags(flags)
            .for_all_objects()
            .with_aggregations([kpis.Aggregations.Mean])
            .build()
        )

    def _create_flow_kpi_definitions(self) -> list:
        return (
            kpis.FlagAggKPIBuilder()
            .for_flag('country_borders_t.net_flow')
            .for_objects_with_model_properties(properties=dict(name_is_alphabetically_sorted=True))
            .with_aggregations([kpis.Aggregations.Mean])
            .build()
        )

    def _add_kpis_to_study(self, scenario_defs: list = None, comparison_defs: list = None) -> None:
        if scenario_defs:
            self._study.scen.add_kpis_from_definitions_to_all_child_datasets(scenario_defs)
        if comparison_defs:
            self._study.comp.add_kpis_from_definitions_to_all_child_datasets(comparison_defs)


class MapGenerator(folviz.CustomKPIGroupGenerator):
    """
    Custom group generator that creates 2 groups per dataset:
    - Prices + Flows
    - Net Positions + Flows

    Flows appear in both groups. Each KPI type has its own visualization style.
    All generator setup and legend management is encapsulated within this class.
    """

    def __init__(self):
        """Initialize colormaps and generators for all KPI types."""
        self.price_colormap = self._create_price_colormap()
        self.netpos_colormap = self._create_netpos_colormap()
        self.flow_colormap = self._create_flow_colormap()

        self.price_generators = self._get_price_generators()
        self.net_position_generators = self._get_net_position_generators()
        self.flow_generators = self._get_flow_arrow_generators()

    def _create_price_colormap(self) -> valmap.SegmentedContinuousColorscale:
        return valmap.SegmentedContinuousColorscale(
            segments={
                (0, 100): theme.colors.sequential.default,
            },
            nan_fallback='#A2A2A2',
        )

    def _create_netpos_colormap(self) -> valmap.SegmentedContinuousColorscale:
        return valmap.SegmentedContinuousColorscale(
            segments={
                (-15_000, 15_000): theme.colors.diverging.teal_amber[::-1],
            },
            nan_fallback='#A2A2A2',
        )

    def _create_flow_colormap(self) -> valmap.SegmentedContinuousColorscale:
        return valmap.SegmentedContinuousColorscale(
            segments={
                (0, 5_000): ['#101010', '#000000'],
            },
            nan_fallback='#A2A2A2',
        )

    def _get_price_generators(self) -> List[folviz.FoliumObjectGenerator]:
        area_gen = folviz.AreaGenerator(
            folviz.AreaFeatureResolver(
                fill_color=folviz.PropertyMapper.from_kpi_value(self.price_colormap),
                fill_opacity=1.0,
                border_color='#ffffff',
                border_width=2,
                tooltip=True
            )
        )

        text_gen = self._create_area_text_generator(self.price_colormap)

        return [area_gen, text_gen]

    def _get_net_position_generators(self) -> List[folviz.FoliumObjectGenerator]:
        area_gen = folviz.AreaGenerator(
            folviz.AreaFeatureResolver(
                fill_color=folviz.PropertyMapper.from_kpi_value(self.netpos_colormap),
                fill_opacity=1.0,
                border_color='#ffffff',
                border_width=2,
                tooltip=True
            )
        )

        text_gen = self._create_area_text_generator(self.netpos_colormap)

        return [area_gen, text_gen]

    def _get_flow_arrow_generators(self) -> List[folviz.FoliumObjectGenerator]:
        from captain_arro import ArrowTypeEnum

        width_mapping = lambda x: np.interp(x, [0, 9.9, 10, 5_000], [1, 1, 10, 30])
        height_mapping = lambda x: width_mapping(x * 4 / 3)

        arrow_gen = folviz.ArrowIconGenerator(
            folviz.ArrowIconFeatureResolver(
                arrow_type=ArrowTypeEnum.MOVING_FLOW_ARROW,
                color=folviz.PropertyMapper.from_kpi_value(self.flow_colormap, use_abs_kpi_value=True),
                reverse_direction=folviz.PropertyMapper.from_kpi_value(lambda v: v < 0),
                stroke_width=2,
                width=folviz.PropertyMapper.from_kpi_value(width_mapping, use_abs_kpi_value=True),
                height=folviz.PropertyMapper.from_kpi_value(height_mapping, use_abs_kpi_value=True),
                speed_in_duration_seconds=4,
                speed_in_px_per_second=None,
                num_arrows=4,
            )
        )

        return [arrow_gen]

    def _create_area_text_generator(self, colormap) -> folviz.TextOverlayGenerator:
        """
        Create text overlay generator with color-adaptive text.

        Args:
            colormap: Colormap to use for determining text color contrast

        Returns:
            Configured TextOverlayGenerator
        """
        def format_text(item: folviz.KPIDataItem) -> str:
            return f'{round(item.kpi.value)}'

        def text_color(item: folviz.KPIDataItem) -> str:
            area_color = colormap(item.kpi.value)
            r, g, b = [int(area_color[i:i + 2], 16) for i in (1, 3, 5)]
            is_dark = (0.299 * r + 0.587 * g + 0.114 * b) < 150
            return '#F2F2F2' if is_dark else '#194D6C'

        return folviz.TextOverlayGenerator(
            folviz.TextOverlayFeatureResolver(
                text_print_content=folviz.PropertyMapper(format_text),
                font_size='10pt',
                text_color=folviz.PropertyMapper(text_color),
                shadow_color=None,
                location=folviz.PropertyMapper.from_item_attr('projection_point')
            )
        )

    def add_legends_to_map(self, map_obj: folium.Map) -> None:
        price_legend = folviz.legends.ContinuousColorscaleLegend(
            mapping=self.price_colormap,
            title='Mean Price [€/MWh]',
            background_color='white',
            width=250,
            segment_height=20,
            position=dict(bottom=20, right=20),
            padding=20,
            n_ticks_per_segment=2,
        )
        price_legend.add_to(map_obj)

        netpos_legend = folviz.legends.ContinuousColorscaleLegend(
            mapping=self.netpos_colormap,
            title='Mean Net Position [MW]',
            background_color='white',
            width=250,
            segment_height=20,
            position=dict(bottom=130, right=20),  # Offset from price legend
            padding=20,
            n_ticks_per_segment=2,
        )
        netpos_legend.add_to(map_obj)

        flow_legend = folviz.legends.ContinuousColorscaleLegend(
            mapping=self.flow_colormap,
            title='Mean Flow [MW]',
            background_color='white',
            width=250,
            segment_height=20,
            position=dict(bottom=240, right=20),  # Offset from price legend
            padding=20,
            n_ticks_per_segment=2,
        )
        flow_legend.add_to(map_obj)

    def add_non_physical_interconnector_cables_to_map(self, study: StudyManager, map_obj: folium.Map) -> None:
        country_borders = study.scen.get_dataset().fetch('country_borders')
        _mask = (~ country_borders['is_physical']) & country_borders['name_is_alphabetically_sorted']
        borders_to_visualize = country_borders.loc[_mask]

        line_generator = folviz.LineGenerator(
            folviz.LineFeatureResolver(
                line_color='#ABABAB',
                line_width=3,
                tooltip=False,
                popup=False,
                geometry=PropertyMapper.from_item_attr('geo_line_string')
            )
        )
        border_fg = folium.FeatureGroup('Country Border lines', overlay=True, control=True)
        border_fg = line_generator.generate_objects_for_model_df(borders_to_visualize, border_fg)
        border_fg.add_to(map_obj)

    def create_kpi_groups_with_names(self, source: StudyManager) -> List[tuple[str, KPICollection]]:
        """
        Create dual groups (Prices + Flows, Net Positions + Flows) for each dataset.

        Args:
            source: StudyManager instance to iterate through datasets

        Returns:
            List of (group_name, kpi_collection) tuples
        """
        groups = []

        for dataset in source.scen.dataset_iterator:
            kpi_col: KPICollection = dataset.kpi_collection

            price_kpis = kpi_col.filter(flag='countries_t.vol_weighted_marginal_price')
            netpos_kpis = kpi_col.filter(flag='countries_t.net_position')
            flow_kpis = kpi_col.filter(flag='country_borders_t.net_flow')

            agg = price_kpis._kpis[0].attributes.aggregation if price_kpis else 'mean'

            if not price_kpis.empty:
                price_group = price_kpis + flow_kpis
                group_name = f"Prices - {dataset.name} [{agg}]"
                groups.append((group_name, price_group))

            if not netpos_kpis.empty:
                netpos_group = netpos_kpis + flow_kpis
                group_name = f"Net Positions - {dataset.name} [{agg}]"
                groups.append((group_name, netpos_group))

        return list(sorted(groups))

    def get_generators_for_kpi(self, kpi: KPI) -> List[folviz.FoliumObjectGenerator]:
        flag = kpi.attributes.flag

        if 'vol_weighted_marginal_price' in flag:
            return self.price_generators

        elif 'net_position' in flag:
            return self.net_position_generators

        elif 'net_flow' in flag:
            return self.flow_generators

        raise NotImplementedError(f'No rule defined for flag {flag}.')

    def initialize_map(self, study: StudyManager) -> folium.Map:
        """Initialize base folium map with country backgrounds."""
        m = folium.Map(location=[52, 15], tiles=None, zoom_start=4.5, zoom_snap=0.25)
        set_background_color_of_map(m, color='#ffffff')

        country_plotter = MapCountryPlotter()
        countries_included = study.scen.get_dataset().fetch('countries').index.to_list()
        country_plotter.add_all_countries_except(
            folium.FeatureGroup(name="World"),
            countries_included,
            style=dict(fillColor='#D9D9D9'),
        ).add_to(m)
        return m


if __name__ == '__main__':
    study: StudyManager
    (study, )

    output_folder = STUDY_FOLDER.joinpath('dvc/output/figs_map')
    os.makedirs(output_folder, exist_ok=True)

    KPISetup(study).run()
    map_gen = MapGenerator()
    m = map_gen.initialize_map(study)
    map_gen.add_legends_to_map(m)
    map_gen.generate_and_add_feature_groups_to_map(source=study, map_obj=m, show='first')
    map_gen.add_non_physical_interconnector_cables_to_map(study, m)

    # Add layer control and save
    folium.LayerControl(collapsed=False, draggable=True).add_to(m)
    m.save(output_folder.joinpath('map.html'))

    print(f"Dual-group map saved to: {output_folder.joinpath('map.html')}")
