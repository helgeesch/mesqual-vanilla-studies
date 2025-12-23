from pathlib import Path
import pandas as pd

pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max_rows', 5)
pd.set_option('display.max_columns', 5)

from studies.study_01_intro_to_mesqual.scripts.setup_study_manager import get_scigrid_de_study_manager

STUDY_FOLDER = Path('studies/study_01_intro_to_mesqual')

study = get_scigrid_de_study_manager()

# %% Access scenario data across all scenarios
scenario_prices = study.scen.fetch('buses_t.marginal_price')
print(scenario_prices)  # Print price time-series df for all scenarios concatenated with MultiIndex

# %% Access comparison deltas automatically calculated across all comparisons
price_changes = study.comp.fetch('buses_t.marginal_price')
print(price_changes)  # Print price time-series df for all comparisons concatenated with MultiIndex

# %% Access unified view with type-level distinction
unified_scen_and_comp_price_data = study.scen_comp.fetch('buses_t.marginal_price')
print(unified_scen_and_comp_price_data)  # Print price time-series df for all scenarios and comparisons concatenated with additional level on MultiIndex:

# %% Access to data from individual scenario
ds_base = study.scen.get_dataset('base')
base_prices = ds_base.fetch('buses_t.marginal_price')
print(base_prices)  # Print price time-series df for base scenario

# %%
base_buses_model_df = ds_base.fetch('buses').iloc[:, :-10]
print(base_buses_model_df)  # Print bus model df for base scenario

# %%
base_generation = ds_base.fetch('generators_t.p')
print(base_generation)  # Print generation time-series df for base scenario

# %% Access to individual comparison dataset
ds_comp_high_res = study.comp.get_dataset('high_res vs base')
price_changes_high_res = ds_comp_high_res.fetch('buses_t.marginal_price')
print(price_changes_high_res)  # Print price time-series df changes (deltas) comparing high_res to base

# %%
bus_model_changes_high_res = ds_comp_high_res.fetch('buses').iloc[:, :-10]
print(bus_model_changes_high_res)  # Print bus model df changes comparing high_res to base

# %% Access merged dataframe (useful to get unified model_df in case of different objects across scenarios)
bus_model_df_merged = study.scen.fetch_merged('buses').iloc[:, :-10]
print(bus_model_df_merged)  # Print merged bus model df for all scenarios

# %%
from mesqual.kpis import FlagAggKPIBuilder, Aggregations, ComparisonKPIBuilder, ValueComparisons
# Clear any existing KPIs
study.scen.clear_kpi_collection_for_all_child_datasets()
study.comp.clear_kpi_collection_for_all_child_datasets()

# Get base dataset to access control areas
ds_base = study.scen.get_dataset('base')
generators = ds_base.fetch('generators').query("carrier.isin(['Gas', 'Hard Coal', 'Brown Coal'])").index.to_list()

# Define scenario KPIs using KPI system

market_price_definitions = (
    FlagAggKPIBuilder()
    .for_flag('control_areas_t.vol_weighted_marginal_price')
    .with_aggregation(Aggregations.Mean)
    .build()
)

# Generation capacity utilization KPIs
generation_definitions = (
    FlagAggKPIBuilder()
    .for_flag('generators_t.p')
    .with_aggregation(Aggregations.Mean)
    .build()  # .for_all_objects() is default
)
kpi_defs = market_price_definitions + generation_definitions
study.scen.add_kpis_from_definitions_to_all_child_datasets(kpi_defs)
print(f"Added KPIs to scenario datasets.")

# Define comparison KPIs (calculate changes between scenarios)
print("\nGenerating comparison KPIs...")
comparison_defs = (
    ComparisonKPIBuilder(kpi_defs)
    .with_comparisons([
        ValueComparisons.Increase,  # Absolute change
        ValueComparisons.Delta      # Also Delta for compatibility
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
import folium

from mesqual.visualizations.value_mapping_system import SegmentedContinuousColorscale
import mesqual.visualizations.folium_viz_system as folviz
from mesqual.utils.folium_utils import set_background_color_of_map
from mesqual.visualizations.folium_viz_system import (
    AreaGenerator,
    AreaFeatureResolver,
    KPICollectionMapVisualizer,
    PropertyMapper,
    TextOverlayGenerator,
)
from mesqual.utils.plotly_utils.plotly_theme import colors
price_colorscale = SegmentedContinuousColorscale(
    segments={
        (-25, 0): colors.sequential.shades_of_blue[::-1],
        (0, 25): colors.sequential.shades_of_pink,
    },
    nan_fallback='#CCCCCC'
)

# Create map
m1 = folium.Map(
    location=[51, 11],
    zoom_start=6,
    tiles=None
)
m1 = set_background_color_of_map(m1, color='#ffffff')

# Add legend
folviz.legends.ContinuousColorscaleLegend(
    mapping=price_colorscale,
    title="Market Price (€/MWh)",
    width=300,
    position={'bottom': 50, 'right': 50}
).add_to(m1)

# Create area generator with KPI-based coloring
price_area_generator = AreaGenerator(
    AreaFeatureResolver(
        fill_color=PropertyMapper.from_kpi_value(price_colorscale),
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

# Use KPICollectionMapVisualizer for automatic visualization
KPICollectionMapVisualizer(
    generators=[price_area_generator, TextOverlayGenerator()]
).generate_and_add_feature_groups_to_map(price_kpis, m1, show='last')

folium.LayerControl(collapsed=False).add_to(m1)

m1.save('_tmp/map_test.html')

# %%