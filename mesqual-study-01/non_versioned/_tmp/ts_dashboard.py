import pandas as pd

from mesqual.visualizations.plotly_figures.timeseries_dashboard import TimeSeriesDashboardGenerator

url = "https://tubcloud.tu-berlin.de/s/pKttFadrbTKSJKF/download/time-series-lecture-2.csv"
ts_raw = pd.read_csv(url, index_col=0, parse_dates=True).rename_axis('variable', axis=1)
ts_res = ts_raw[['onwind', 'offwind', 'solar']]

# generator_raw = TimeSeriesDashboardGenerator(
#     x_axis='date',
#     color_continuous_scale='viridis',
#     facet_col='variable',
#     facet_col_order=['solar', 'onwind', 'offwind']
# )
# fig_raw = generator_raw.get_figure(ts_res*100, title='Variables')
# fig_raw.show(renderer='browser')

# Multiple scenarios
ts_res_scenarios = pd.concat(
    {
        'base': ts_res,
        'scen1': ts_res ** 0.7,
        'scen2': ts_res ** 0.5
    },
    axis=1,
    names=['dataset']
)
ts_res_scenarios = ts_res_scenarios * 100  # to percent
ts_res_scenarios.columns = ts_res_scenarios.columns.reorder_levels([1, 0])

stats = TimeSeriesDashboardGenerator.DEFAULT_STATISTICS.copy()
stats['Std'] = TimeSeriesDashboardGenerator.STATISTICS_LIBRARY['Std']
stats['% == 0'] = TimeSeriesDashboardGenerator.STATISTICS_LIBRARY['% == 0']
generator_res_scenarios = TimeSeriesDashboardGenerator(
    x_axis='date',
    facet_col='dataset',
    facet_row='variable',
    facet_col_order=['scen2', 'base', 'scen1'],
    facet_row_order=['solar', 'onwind', 'offwind'],
    color_continuous_scale='viridis',
)
fig_res_scenarios = generator_res_scenarios.get_figure(ts_res_scenarios, title='Variable per Scenario')
fig_res_scenarios.show(renderer='browser')