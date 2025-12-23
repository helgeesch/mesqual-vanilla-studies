import folium

from mesqual import kpis
import mesqual.visualizations.folium_viz_system as folviz
import mesqual.visualizations.value_mapping_system as valmap
from mesqual.utils.folium_utils.background_color import set_background_color_of_map
from mesqual.utils.plotly_utils.plotly_theme import colors
from vanilla.notebook_config import configure_clean_output_for_jupyter_notebook
from vanilla.conditional_renderer import ConditionalRenderer

configure_clean_output_for_jupyter_notebook()
renderer = ConditionalRenderer()

# Load the StudyManager with PyPSA Scigrid-DE network data
from studies.study_01_intro_to_mesqual.scripts.setup_study_manager import get_scigrid_de_study_manager

study = get_scigrid_de_study_manager()

print("Study scenarios:")
for dataset in study.scen.datasets:
    print(f"  📊 {dataset.name}")

print("\nComparisons:")
for dataset in study.comp.datasets:
    print(f"  🔄 {dataset.name}")

# %%
# Clear any existing KPIs
study.scen.clear_kpi_collection_for_all_child_datasets()
study.comp.clear_kpi_collection_for_all_child_datasets()

# Get base dataset to access control areas
ds_base = study.scen.get_dataset('base')
generators = ds_base.fetch('generators').query("carrier.isin(['Gas', 'Hard Coal', 'Brown Coal'])").index.to_list()

# Define scenario KPIs using KPI system

market_price_definitions = (
    kpis.FlagAggKPIBuilder()
    .for_flag('control_areas_t.vol_weighted_marginal_price')
    .with_aggregation(kpis.Aggregations.Mean)
    .build()
)

# Generation capacity utilization KPIs
generation_definitions = (
    kpis.FlagAggKPIBuilder()
    .for_flag('generators_t.p')
    .with_aggregation(kpis.Aggregations.Mean)
    .build()  # .for_all_objects() is default
)
kpi_defs = market_price_definitions + generation_definitions
study.scen.add_kpis_from_definitions_to_all_child_datasets(kpi_defs)
print(f"Added KPIs to scenario datasets.")

# Define comparison KPIs (calculate changes between scenarios)
print("\nGenerating comparison KPIs...")
comparison_defs = (
    kpis.ComparisonKPIBuilder(kpi_defs)
    .with_comparisons([
        kpis.ValueComparisons.Increase,  # Absolute change
        kpis.ValueComparisons.Delta      # Also Delta for compatibility
    ])
    .build()
)
study.comp.add_kpis_from_definitions_to_all_child_datasets(comparison_defs)
print(f"Added comparison KPIs to comparison datasets")

# Get merged collections
scenario_kpi_collection = study.scen.get_merged_kpi_collection()
comparison_kpi_collection = study.comp.get_merged_kpi_collection()

print(f"\nTotal scenario KPIs: {scenario_kpi_collection.size}")
print(f"Total comparison KPIs: {comparison_kpi_collection.size}")

print("\n✅ All KPIs generated successfully!")

# %%

# Create colorscale for market prices
price_colorscale = valmap.SegmentedContinuousColorscale(
    segments={
        (-25, 0): colors.sequential.shades_of_blue[::-1],
        (0, 25): colors.sequential.shades_of_pink,
    },
    nan_fallback='#CCCCCC'
)

# Create area generator with KPI-based coloring
price_area_generator = folviz.AreaGenerator(
    folviz.AreaFeatureResolver(
        fill_color=folviz.PropertyMapper.from_kpi_value(price_colorscale),
        fill_opacity=0.8,
        border_color='#2c3e50',
        border_width=2,
        tooltip=True  # Auto-generates tooltip with KPI info
    )
)

# Filter KPIs to show only market prices using new API
price_kpis = scenario_kpi_collection.filter_by_kpi_attributes(
    filter_funcs=dict(flag=lambda f: 'price' in f)
)

print(f"Found {price_kpis.size} price KPIs")


# %%
# Create diverging colorscale for price changes
price_change_colormap = valmap.SegmentedContinuousColorscale(
    segments={
        (-10, 0): colors.sequential.shades_of_blue[::-1],
        (0, 10): colors.sequential.shades_of_pink,
    },
    nan_fallback='#CCCCCC'
)

# Create area generator for price changes
price_change_generator = folviz.AreaGenerator(
    folviz.AreaFeatureResolver(
        fill_color=folviz.PropertyMapper.from_kpi_value(price_change_colormap),
        fill_opacity=0.8,
        border_color='#34495e',
        border_width=2,
        tooltip=True
    )
)

# Filter comparison KPIs for price changes using new API
price_change_kpis = comparison_kpi_collection.filter_by_kpi_attributes(
    filter_funcs=dict(flag=lambda f: 'price' in f)
)

# %%
# Create comprehensive map with multiple KPI layers
m3 = folium.Map(
    location=[51, 11],
    zoom_start=6,
    tiles=None
)
m3 = set_background_color_of_map(m3, color='#ffffff')

# Define different colorscales for different KPI types
generation_colorscale = valmap.SegmentedContinuousColorscale.single_segment_autoscale_factory_from_array(
    values=[0, 100],
    color_range='viridis',
)

colorscales = {
    'price': {'pos': {'bottom': 50, 'left': 50}, 'scale': price_colorscale, 'title': "Average Market Price (€/MWh)"},
    'change': {'pos': {'bottom': 200, 'left': 50}, 'scale': price_change_colormap, 'title': "Price Change (€/MWh)"},
    'generation': {'pos': {'bottom': 350, 'left': 50}, 'scale': generation_colorscale, 'title': "Average Generation (MW)"},
}

for k, v in colorscales.items():
    folviz.legends.ContinuousColorscaleLegend(
        mapping=v['scale'],
        title=v['title'],
        width=280,
        position=v['pos']
    ).add_to(m3)

from shapely import Point

# In this case, we don't have a "location" column ready in the generator model df, so we create the location on demand
def _get_location_of_generator(gen_data_item: folviz.VisualizableDataItem) -> Point:
    lat = gen_data_item.get_object_attribute('bus_y')
    lon = gen_data_item.get_object_attribute('bus_x')
    return Point([lon, lat])

# Visualize market prices for scenarios using new filtering API
# price_fgs = (
#     folviz.KPICollectionMapVisualizer(
#         generators=[
#             folviz.AreaGenerator(
#                 folviz.AreaFeatureResolver(
#                     fill_color=folviz.PropertyMapper.from_kpi_value(colorscales['price']['scale']),
#                     fill_opacity=0.8,
#                     border_width=2,
#                     tooltip=True
#                 )
#             ),
#             folviz.TextOverlayGenerator()
#         ]
#     )
#     .generate_and_add_feature_groups_to_map(
#         kpi_collection=scenario_kpi_collection.filter_by_kpi_attributes(filter_funcs=dict(flag=lambda f: 'price' in f)),
#         folium_map=m3,
#         show="none"
#     )
# )

from mesqual.units import QuantityToTextConverter, Units
# Visualize price changes for comparisons - filter by both flag and value_comparison
price_change_fgs = (
    folviz.KPICollectionMapVisualizer(
        generators=[
            folviz.AreaGenerator(
                folviz.AreaFeatureResolver(
                    fill_color=folviz.PropertyMapper.from_kpi_value(colorscales['change']['scale']),
                    fill_opacity=0.8,
                    border_width=2,
                    tooltip=True
                )
            ),
            folviz.TextOverlayGenerator()
        ],
        value_formatting=QuantityToTextConverter(
            Units.EUR_per_MWh,
            decimals=1,
            include_unit=False,
            include_oom=False,
            include_sign=True,
        )
    )
    .generate_and_add_feature_groups_to_map(
        kpi_collection=(
            comparison_kpi_collection
            .filter_by_kpi_attributes(filter_funcs=dict(flag=lambda f: 'price' in f))
            .filter(value_comparison=kpis.ValueComparisons.Increase)
        ),
        folium_map=m3,
        show='first',
    )
)
#
# # Visualize generation for scenarios
# generation_fgs = (
#     folviz.KPICollectionMapVisualizer(
#         generators=[
#             folviz.CircleMarkerGenerator(
#                 folviz.CircleMarkerFeatureResolver(
#                     fill_color=folviz.PropertyMapper.from_kpi_value(colorscales['generation']['scale']),
#                     radius=folviz.PropertyMapper.from_item_attr('p_nom', lambda p: max(min(20, p / 50), 3)),
#                     fill_opacity=0.8,
#                     border_width=1,
#                     tooltip=True,
#                     location=folviz.PropertyMapper(_get_location_of_generator)
#                 )
#             ),
#             folviz.TextOverlayGenerator()
#         ]
#     )
#     .generate_and_add_feature_groups_to_map(
#         kpi_collection=scenario_kpi_collection.filter(flag='generators_t.p'),
#         folium_map=m3,
#         show='first'
#     )
# )
# _empty_fg = folium.FeatureGroup('None', overlay=False, show=False, )
# _empty_fg.add_to(m3)
# generation_fgs = generation_fgs + [_empty_fg]

folium.LayerControl(collapsed=True).add_to(m3)

from folium.plugins import GroupedLayerControl
GroupedLayerControl(
    groups={
        'Area Fgs': price_change_fgs,  # price_fgs + ,
        # 'Generator Fgs': generation_fgs
    },
    exclusive_groups=False,
    collapsed=True,
).add_to(m3)


# renderer.show_folium(m3)
m3.save('_tmp/map.html')