#!/usr/bin/env python3

initial_accum = {'_cif_state_components': set(),
                 '_prom_week_components' : set(),
                 '_cif_library_components' : set(),

                 '_cif_state_counts': {},
                 '_prom_week_counts' : {},
                 '_cif_library_counts' : {},
                 '__all_counts' : {}
                 }

def accumulator(new_data, acc_data, ctx):
    #accumulator descriptions for cifstates, promweeks and ciflibraries

    if 'is_cifstate' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_cif_state_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_cif_state_counts']:
                acc_data['_cif_state_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
                acc_data['__all_counts'][x] += new_data['all_counts'][x]
                acc_data['_cif_state_counts'][x] += new_data['all_counts'][x]

    elif 'is_promweek' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_prom_week_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_prom_week_counts']:
                acc_data['_prom_week_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
                acc_data['__all_counts'][x] += new_data['all_counts'][x]
                acc_data['_prom_week_counts'][x] += new_data['all_counts'][x]

    elif 'is_cif_library' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_cif_library_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_cif_library_counts']:
                acc_data['_cif_library_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
                acc_data['__all_counts'][x] += new_data['all_counts'][x]
                acc_data['_cif_library_counts'][x] += new_data['all_counts'][x]

    return acc_data
