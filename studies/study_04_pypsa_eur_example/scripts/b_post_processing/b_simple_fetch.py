if __name__ == '__main__':
    from mesqual import StudyManager
    study: StudyManager
    (study,)

    flag = 'countries_t.trade_balance_per_partner'

    print(f'Fetching MultiIndex df for flag with all scenarios')
    print(study.scen.fetch(flag).round(2))

    print(f'\n\nFetching MultiIndex df for flag with all comparisons (deltas)')
    print(study.comp.fetch(flag).round(2))

    print(f'\n\nFetching MultiIndex df for flag with all scenarios and comparisons (additional Index-level)')
    print(study.scen_comp.fetch(flag).round(2))
