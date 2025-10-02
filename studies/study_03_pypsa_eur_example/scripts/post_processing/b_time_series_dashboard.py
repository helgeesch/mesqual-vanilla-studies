from mesqual import StudyManager
from mesqual.visualizations import TimeSeriesDashboardGenerator

study: StudyManager

price_color = dict(color_continuous_scale='rainbow', range_color=[0, 100])
price_change_color = dict(color_continuous_scale='PiYG', color_continuous_midpoint=0)
generator = TimeSeriesDashboardGenerator(
    x_axis='date',
    facet_col='dataset',
    facet_row='Bus',  # 'country'
    per_facet_col_colorscale=True,
    facet_col_color_settings={
        'base': price_color,
        'high_res': price_color,
        'cheap_gas': price_color,
        'high_res vs base': price_change_color,
        'cheap_gas vs base': price_change_color,
    },
)

data = study.scen_comp.fetch('buses_t.marginal_price')
data = data[[c for c in data.columns if (c[-1].endswith(' 0') and any(country in c[-1] for country in ['DE', 'ES', 'PT', 'FR']))]]
fig = generator.get_figure(data.droplevel(0, axis=1), _skip_validation=True)
fig.show()