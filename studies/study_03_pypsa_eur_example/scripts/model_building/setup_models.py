import pypsa

n_base = pypsa.Network('studies/study_03_pypsa_eur_example/non_versioned/resources/networks/elec_s_256.nc')
n_base.name = 'base'


SNAPSHOTS = n_base.snapshots[:4]

n_high_res = n_base.copy()
n_high_res.name = 'high_res'
_mask_res = n_high_res.generators['carrier'].isin(['offwind-dc', 'offsind-ac', 'onwind', 'solar'])
n_high_res.generators.loc[_mask_res, 'p_nom_max'] *= 1.5


n_cheap_gas = n_base.copy()
n_cheap_gas.name = 'cheap_gas'
_mask_gas = n_cheap_gas.generators['carrier'].isin(['CCGT', 'OCGT'])
n_cheap_gas.generators.loc[_mask_gas, 'marginal_cost'] *= 0.5

# for n in [n_base, n_high_res, n_cheap_gas]:
for n in [n_base]:
    n.set_snapshots(SNAPSHOTS)
    n.optimize(
        linearized_unit_commitment=True,
        solver_options=dict(time_limit=100)
    )
