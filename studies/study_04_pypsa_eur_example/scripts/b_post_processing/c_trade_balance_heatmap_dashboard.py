from pathlib import Path

from mesqual import StudyManager
from mesqual.visualizations import TimeSeriesDashboardGenerator

from studies.study_04_pypsa_eur_example.src.config import theme


class TradeBalanceTimeSeriesDashbaordGenerator:
    def __init__(self, study_manager: StudyManager):
        self._study = study_manager

    def save_figs(self, folder: Path):
        flag = f'countries_t.trade_balance_per_partner'

        data = self._study.scen_comp.fetch(flag).xs('net_exp', level='variable', axis=1)
        countries = data.columns.get_level_values(-1).unique()
        countries = ['DE', 'AT', 'FR', 'BE']  # shorten
        scenario_names = [s.name for s in self._study.scen.dataset_iterator]

        for country in countries:
            dff = data.xs(country, level=f'primary_country', axis=1)

            max_scen = dff.xs('scenario', level='type', axis=1).abs().max().max()
            dff = dff.droplevel('type', axis=1)
            dff = dff.rename(columns=lambda x: f'NetPosition <b>{country} to {x}</b>', level=-1)

            title = f'{country}: El. Net-Positions to Partners [MW]'
            gen = TimeSeriesDashboardGenerator(
                x_axis='week',
                facet_col='dataset',
                facet_row=f'partner_country',
                color_continuous_scale=theme.colors.diverging.teal_amber,
                per_facet_col_colorscale=True,
                facet_col_color_settings={
                    s: {'range_color': [-max_scen, max_scen]}
                    for s in scenario_names
                },
            )
            fig_area = gen.get_figure(dff, title=title)
            output_file = folder.joinpath(f'{country}_trade_bal_ts.html')
            fig_area.write_html(output_file)


if __name__ == '__main__':
    from studies.study_04_pypsa_eur_example.src.config import STUDY_FOLDER

    study: StudyManager
    (study, )

    output_folder = STUDY_FOLDER.joinpath(f'dvc/output/figs_trade_balance/country_heat_ts')
    output_folder.mkdir(parents=True, exist_ok=True)

    generator = TradeBalanceTimeSeriesDashbaordGenerator(study)
    generator.save_figs(output_folder)
