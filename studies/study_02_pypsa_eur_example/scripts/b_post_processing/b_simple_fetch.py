if __name__ == '__main__':
    from mesqual import StudyManager
    study: StudyManager
    (study,)

    flag = 'countries_t.trade_balance_per_partner'

    print(f'\n\n', '='*50, '\n')

    print(f'All scenarios → MultiIndex DataFrame\n')
    print(study.scen.fetch(flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Individual scenario\n')
    print(study.scen.get_dataset('base').fetch(flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'All comparisons (deltas) → same interface\n')
    print(study.comp.fetch(flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Combined fetch: scenarios + comparisons (additional Index-level)\n')
    print(study.scen_comp.fetch(flag).round(2))
