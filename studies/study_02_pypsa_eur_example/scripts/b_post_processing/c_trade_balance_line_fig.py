if __name__ == '__main__':
    import pandas as pd
    import plotly.express as px

    from mesqual import StudyManager
    from mesqual.utils.pandas_utils import flatten_df

    from studies.study_02_pypsa_eur_example.src.config import STUDY_FOLDER

    study: StudyManager
    (study, )

    output_folder = STUDY_FOLDER.joinpath('dvc/output/figs_trade_balance/country_line_ts')
    output_folder.mkdir(parents=True, exist_ok=True)

    data = study.scen.fetch('countries_t.trade_balance_per_partner') / 1e3
    data = data.xs('net_exp', level='variable', axis=1)
    data = flatten_df(data)
    countries = data['primary_country'].unique()
    countries = ['BE']  # demo only

    for country in countries:
        fig = px.line(
            data[data['primary_country'] == country],
            x='snapshot',
            y='value',
            color='partner_country',
            line_dash='dataset',
            title=f'{country} Net-Positions [GW]'
        )
        max_date = data["snapshot"].max()
        one_week_ago = max_date - pd.Timedelta(days=7)
        fig.update_layout(
            xaxis=dict(
                range=[one_week_ago, max_date],
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1day", step="day", stepmode="backward"),
                        dict(count=7, label="1week", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        fig.write_html(output_folder.joinpath(f'{country}_trade_bal_line_ts.html'))
