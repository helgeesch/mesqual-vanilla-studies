import pypsa

from vanilla.study_path_manager import PathManager

pm = PathManager('studies/study_01_intro_to_mesqual')

pm.ensure_dir(pm.data('networks_scigrid_de'))


# %% DE Base Network
n_base = pypsa.examples.scigrid_de(from_master=True)
n_base.name = 'base'
n_base.optimize()
n_base.export_to_netcdf(pm.data('networks_scigrid_de/base.nc'))

# %% DE high RES scenarios
for carrier in ['wind', 'solar']:
    for factor in [150, 200]:
        n_high_res = pypsa.examples.scigrid_de(from_master=True)
        n_high_res.name = f'{carrier}_{factor}'
        _mask_wind = n_high_res.generators['carrier'].str.lower().str.contains(carrier)
        n_high_res.generators.loc[_mask_wind, 'p_nom'] *= factor / 100
        n_high_res.optimize()
        n_high_res.export_to_netcdf(pm.data(f'networks_scigrid_de/{n_high_res.name}.nc'))
