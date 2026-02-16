if __name__ == '__main__':
    from mesqual import StudyManager
    study: StudyManager
    (study,)

    model_flag = 'countries'
    result_flag = 'countries_t.trade_balance_per_partner'

    print(f'\n\n', '='*50, '\n')

    print(f'Results: All scenarios → MultiIndex DataFrame\n')
    print(study.scen.fetch(result_flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Results: Individual scenario\n')
    print(study.scen.get_dataset('base').fetch(result_flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Model: Individual scenario\n')
    print(study.scen.get_dataset('base').fetch(model_flag))

    print(f'\n\n', '='*50, '\n')

    print(f'Results: All comparisons (deltas) → same interface\n')
    print(study.comp.fetch(result_flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Results: Combined fetch: scenarios + comparisons (additional Index-level)\n')
    print(study.scen_comp.fetch(result_flag).round(2))

    print(f'\n\n', '='*50, '\n')

    print(f'Results: Combined fetch: scenarios + comparisons (additional Index-level)\n')
    print(study.scen_comp.fetch(result_flag).round(2))
