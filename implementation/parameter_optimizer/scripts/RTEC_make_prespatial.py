#!/usr/bin/python3


import argparse
import os
import json
from time import time

from termcolor import colored as col


def dict_union(d1, d2):
    """Returns the "union" of two dictionaries.
    Raises error if any fields are different, except for the flags fiels,
    which is a dicitonary whose values are boolean. For these values only,
    it stores their OR value.
    """

    res = {}

    for k in d1:
        if k != 'flags':
            if d1[k] != d2[k]:
                print('different', k, d1[k], d2[k])
                raise RuntimeError
            res[k] = d1[k]
        # If k == 'flags' do or of the fields
        else:
            res[k] = {}
            for kk in d1[k]:
                res[k][kk] = d1[k][kk] or d2[k][kk]

    return res


my_parser = argparse.ArgumentParser(description='Script tha given a dataset creates the files for spatial preprocessing and the ones that will be used to create RTEC\'s input.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir(
                           '../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('The dataset to use.\n', 'cyan'))

args = my_parser.parse_args()
dataset = args.dataset

# Holds the data for the files that will have only crit points
data = {}
# Holds the data for the files that will have crit points + original dataset (this is called enriched dataset)
enriched_data = {}

cur_t = time()

for file_name in os.listdir('tmp_RTEC/'):

    # Ignore not relevant files
    if dataset not in file_name:
        continue

    if 'noiseless' in file_name:
        continue

    if 'synopses' not in file_name:
        continue

    file_name = 'tmp_RTEC/' + file_name

    for l in open(file_name):
        # Load the line as a dictionary
        dic = json.loads(l)

        # Erase useless fields to save memory
        del dic['time_elapsed']
        del dic['ingestion_timestamp']
        del dic['msg_error_flag']
        del dic['distance']
        del dic['heading_diff']
        del dic['percental_speed_change']

        # Rename some fields
        dic['t'] = dic.pop('timestamp')
        dic['lon'] = dic.pop('longitude')
        dic['lat'] = dic.pop('latitude')
        dic['flags'] = dic.pop('annotation')

        # Turn timestamp to seconds
        dic['t'] = dic['t']//1000
        idd = dic['id']

        # Create key. In the enbd there should be only one entry per key,
        # but in the files there arte multiple lines that have the same key (these should be merged).
        key = (dic['t'], dic['lon'], dic['lat'])

        # Create a dict for this id
        if idd not in data:
            data[idd] = {}

        # If first instance of key, simply copy the dictionary
        if key not in data[idd]:
            data[idd][key] = dic
        # Else if key already exists merge the dictionaries
        else:
            data[idd][key] = dict_union(dic, data[idd][key])

        # Do the same for the enriched data
        if idd not in enriched_data:
            enriched_data[idd] = {}

        if key not in enriched_data[idd]:
            enriched_data[idd][key] = dic
        else:
            enriched_data[idd][key] = dict_union(
                dic, enriched_data[idd][key])

    # Open the noiseless file to append the extra data to the enridched data
    for l in open(file_name.replace('.json', '_noiseless.json')):
        dic = json.loads(l)
        del dic['time_elapsed']
        del dic['ingestion_timestamp']
        del dic['msg_error_flag']
        del dic['distance']
        del dic['heading_diff']
        del dic['percental_speed_change']

        dic['t'] = dic.pop('timestamp')
        dic['lon'] = dic.pop('longitude')
        dic['lat'] = dic.pop('latitude')
        dic['flags'] = dic.pop('annotation')

        dic['t'] = dic['t']//1000
        idd = dic['id']
        key = (dic['t'], dic['lon'], dic['lat'])

        # Same process as before
        if idd not in enriched_data:
            enriched_data[idd] = {}

        if key not in enriched_data[idd]:
            enriched_data[idd][key] = dic
        else:
            enriched_data[idd][key] = dict_union(
                dic, enriched_data[idd][key])


print(f'Read synopses files in {time()-cur_t:.1f} seconds.')

# Original dataset to append true heading
if dataset == 'brest':
    file_name = '../../data/brest/nari_dynamic.csv'
else:
    raise NotImplementedError('dataset not implemented yet')

cur_t = time()
first = True
d = {}

for l in open(file_name):

    w = l.replace('\n', '').split(',')

    # First line contains column names
    if first:
        first = False
        for i in range(len(w)):
            # `d` maps column name to index
            d[w[i]] = i
        continue

    idd = w[d['sourcemmsi']]
    t = int(w[d['t']])
    lon = float(w[d['lon']])
    lat = float(w[d['lat']])

    key = (t, lon, lat)

    # If entry exists in data and enriched data (thus it is not noise), append true heading
    if idd in data and key in data[idd]:
        data[idd][key]['trueheading'] = float(w[d['trueheading']])

    if idd in enriched_data and key in enriched_data[idd]:
        enriched_data[idd][key]['trueheading'] = float(w[d['trueheading']])

print(f"Added trueheading in {time()-cur_t:.1f} seconds.")

# Do the same process for enriched and not enriched data
for enriched in [False, True]:

    if enriched:
        DATA = enriched_data
    else:
        DATA = data

    cur_t = time()

    # `final` contains all the data in a list (to be sorted)
    final = []
    for dic in DATA.values():
        for dic2 in dic.values():
            final.append(dic2)

    # Sort list according to timestamp
    final.sort(key=lambda tt: tt['t'])

    print(f"Sorted the {'enriched ' if enriched else ''}data in {time()-cur_t:.1f} seconds.")

    cur_t = time()

    # Location of file that will be used for spatial preprocessing
    if enriched:
        file_name = f'tmp_RTEC/{dataset}_enriched.spatial.csv'
    else:
        file_name = f'tmp_RTEC/{dataset}_critical.spatial.csv'

    with open(file_name, 'w') as f:

        for d in final:
            f.write(
                f"HappensAt [coord <{d['id']}> {d['lon']:.9f} {d['lat']:.9f}] {d['t']}\n"
            )
            f.write(
                f"HappensAt [velocity <{d['id']}> {d['speed']*1.852:.9f} {d['heading']:.9f}] {d['t']}\n"
            )
            if d['flags'].get('gap_start', False):
                f.write(
                    f"HappensAt [gap_start <{d['id']}> {d['speed']*1.852:.9f} {d['heading']:.9f}] {d['t']}\n")

    print(
        f"Made pre-spatial {'enriched ' if enriched else ''}data in {time()-cur_t:.1f} seconds.")

    cur_t = time()
    if enriched:
        file_name = f'tmp_RTEC/{dataset}_enriched_without_spatial.csv'
    else:
        file_name = f'tmp_RTEC/{dataset}_critical_without_spatial.csv'

    events = [
        'change_in_speed_start',
        'change_in_speed_end',
        'change_in_heading',
        'stop_start',
        'stop_end',
        'slow_motion_start',
        'slow_motion_end',
        'gap_start',
        'gap_end'
    ]

    with open(file_name, 'w') as f:

        for d in final:
            f.write(
                f"coord|{d['t']}|{d['t']}|{d['id']}|{d['lon']:.9f}|{d['lat']:.9f}\n"
            )
            f.write(
                f"velocity|{d['t']}|{d['t']}|{d['id']}|{d['speed']:.9f}|{d.get('heading', 0.0):.9f}|{d.get('trueheading', 0.0):.9f}\n"
            )

            for event in events:
                if d['flags'].get(event, False):
                    f.write(f"{event}|{d['t']}|{d['t']}|{d['id']}\n")

    print(
        f"Made without spatial {'enriched ' if enriched else ''}data in {time()-cur_t:.1f} seconds.")
