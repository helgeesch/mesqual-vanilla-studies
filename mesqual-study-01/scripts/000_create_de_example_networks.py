import pypsa

from studies.study_01_intro_to_mesqual.src.config import STUDY_FOLDER

networks_folder = STUDY_FOLDER.joinpath('data/networks_scigrid_de')
networks_folder.mkdir(parents=True, exist_ok=True)

# %% DE Base Network
n_base = pypsa.examples.scigrid_de(from_master=True)
n_base.name = 'base'
n_base.optimize()
n_base.export_to_netcdf(networks_folder('base.nc'))

# %% DE high RES scenarios
for carrier in ['wind', 'solar']:
    for factor in [150, 200]:
        n_high_res = pypsa.examples.scigrid_de(from_master=True)
        n_high_res.name = f'{carrier}_{factor}'
        _mask_wind = n_high_res.generators['carrier'].str.lower().str.contains(carrier)
        n_high_res.generators.loc[_mask_wind, 'p_nom'] *= factor / 100
        n_high_res.optimize()
        n_high_res.export_to_netcdf(networks_folder('{n_high_res.name}.nc'))
