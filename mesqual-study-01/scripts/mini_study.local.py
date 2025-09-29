import os
import pypsa
import pandas as pd

pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max_rows', 5)
pd.set_option('display.max_columns', 5)

# %%
study_folder = 'studies/study_01_intro_to_mesqual'
networks_folder = os.path.join(study_folder, 'data/networks_scigrid_de')

n_base = pypsa.Network(os.path.join(networks_folder, 'base.nc'))
n_high_res = pypsa.Network(os.path.join(networks_folder, 'solar_150.nc'))
n_cheap_gas = pypsa.Network(os.path.join(networks_folder, 'wind_200.nc'))

# %%
from mesqual import StudyManager
from mesqual_pypsa import PyPSADataset

study = StudyManager.factory_from_scenarios(
    scenarios = [
             PyPSADataset(n_base, name='base'),
             PyPSADataset(n_high_res, name='high_res'),
             PyPSADataset(n_cheap_gas, name='n_cheap_gas'),
    ],
comparisons = [('high_res', 'base'), ('n_cheap_gas', 'base')],  # StudyManager handles automatic naming with '*variation_dataset_name* vs *reference_dataset_name*'
)


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
