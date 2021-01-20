#!/usr/bin/python3

import argparse
import json
from math import isnan

from termcolor import colored as col
from tqdm import tqdm


def dict_union(d1, d2):
    """Returns the union of two dictionaries"""

    res = {}

    for k in d1:
        if k != 'annotation':
            if k == 'heading_diff' and min(d1[k], d2[k]) == -1.0:
                d1[k] = max(d1[k], d2[k])
            elif isinstance(d1[k], float) and isinstance(d2[k], float) and isnan(d1[k]) and isnan(d2[k]):
                pass
            elif d1[k] != d2[k]:
                print('different', k, d1[k], d2[k])
                raise RuntimeError
            res[k] = d1[k]
        else:
            res[k] = {}
            for kk in d1[k]:
                res[k][kk] = d1[k][kk] or d2[k][kk]

    return res


my_parser = argparse.ArgumentParser(description='Script tha given a dataset runs the synopses for all types. Uses folders in ../../data/<dataset>/data_per_type/all/',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('--angle_threshold', '-a',
                       type=float,
                       default=4.0,
                       help=col('Angle Threshold for turning critical points.\n', 'cyan'))

my_parser.add_argument('--speed_ratio', '-s',
                       type=float,
                       default=0.25,
                       help=col('Speed Ratio for change in speed critical points.\n', 'cyan'))

my_parser.add_argument('--no_speed_threshold', '-no_s',
                       type=float,
                       default=0.5,
                       help=col('No Speed Threshold for stopped critical points.\n', 'cyan'))

my_parser.add_argument('--distance_threshold', '-d',
                       type=float,
                       default=50.,
                       help=col('No Speed Threshold for stopped critical points.\n', 'cyan'))

my_parser.add_argument('files',
                       type=str,
                       nargs='+',
                       help=col('Files to relabel.\n', 'cyan'))

args = my_parser.parse_args()
angle_thresh = args.angle_threshold
speed_rat = args.speed_ratio
no_speed_thresh = args.no_speed_threshold
dist_thresh = args.distance_threshold
files = args.files

files_tqdm = tqdm(files, desc='Type ?')
max_len = max(map(len, files)) + 1

for name in files_tqdm:

    files_tqdm.set_description(name + ' '*(max_len - len(name)))
    files_tqdm.refresh()

    data = {}

    for l in open(name):
        dic = json.loads(l)

        idd = dic['id']
        key = (dic['timestamp'], dic['longitude'], dic['latitude'])

        if idd not in data:
            data[idd] = {}

        if key not in data[idd]:
            data[idd][key] = dic
        else:
            data[idd][key] = dict_union(dic, data[idd][key])

    input_dictionaries = []
    for dic in data.values():
        for dic2 in dic.values():
            input_dictionaries.append(dic2)

    # Sort input because it might not be sorted
    input_dictionaries.sort(key=lambda y: y['timestamp'])

    # Previous state for each ship
    state = {}

    for dic in input_dictionaries:

        if dic['annotation']['gap_end']:

            dic['annotation']['change_in_speed_start'] = False
            dic['annotation']['change_in_speed_end'] = False

            dic['annotation']['change_in_speed_start'] = False
            dic['annotation']['change_in_speed_end'] = False

            dic['annotation']['stop_start'] = False
            dic['annotation']['stop_end'] = False

            dic['annotation']['stop_start'] = False
            dic['annotation']['stop_end'] = False

            state[dic['id']] = {
                'stopped': False,
                'speed_change': False,
                'prev_dic': dic
            }

            continue

        # Local variable change_in_heading if heading changed
        # Actual change in heading flagged is also control by whether ship is stopped.
        change_in_heading = dic['heading_diff'] > angle_thresh

         # Local variable stopped if speed is lower than threshold
        try:
            if dic['id'] in state and state[dic['id']]['stopped'] and dic['distance'] >= dist_thresh:
                stopped = False
            elif dic['speed'] == 'Infinity':
                stopped = False
            elif dic['speed'] == 'NaN': # NaN = 0/0
                stopped = True
            else:
                stopped = dic['speed'] < no_speed_thresh
        except:
            print('Unknown float value', dic['speed'])
            raise

        # Local variable speed_change if speed is changing
        try:
            if stopped:
                speed_change = False
            elif dic['percental_speed_change'] == -1:
                speed_change = False
            elif dic['percental_speed_change'] == 'Infinity':
                speed_change = True
            elif dic['percental_speed_change'] == 'NaN': # NaN = 0/0
                speed_change = False
            else:
                speed_change = dic['percental_speed_change'] > speed_rat
        except:
            print('Unknown float value', dic['percental_speed_change'])
            raise

        # Assume change in heading in CURRENT posiotion is controlled by change_in_heading flag
        # As seen next this might be false if the next position is stopped
        dic['annotation']['change_in_heading'] = change_in_heading

        # If current position is stopped, change_in_heading in the previous position is False
        if stopped and dic['id'] in state:
            state[dic['id']]['prev_dic']['annotation']['change_in_heading'] = False

        # If first time we see this id
        if dic['id'] not in state:
            dic['annotation']['change_in_speed_start'] = speed_change
            dic['annotation']['change_in_speed_end'] = False

            dic['annotation']['stop_start'] = stopped
            dic['annotation']['stop_end'] = False
        else:
            if state[dic['id']]['speed_change'] == speed_change:
                dic['annotation']['change_in_speed_start'] = False
                dic['annotation']['change_in_speed_end'] = False
            else:
                dic['annotation']['change_in_speed_start'] = speed_change
                dic['annotation']['change_in_speed_end'] = not speed_change

            if state[dic['id']]['stopped'] == stopped:
                dic['annotation']['stop_start'] = False
                dic['annotation']['stop_end'] = False
            else:
                dic['annotation']['stop_start'] = stopped
                dic['annotation']['stop_end'] = not stopped

        state[dic['id']] = {
            'stopped': stopped,
            'speed_change': speed_change,
            'prev_dic': dic
        }


    with open(name, 'w') as f:
        for dic in input_dictionaries:
            f.write(json.dumps(dic))
            f.write('\n')

    del state
    del input_dictionaries
