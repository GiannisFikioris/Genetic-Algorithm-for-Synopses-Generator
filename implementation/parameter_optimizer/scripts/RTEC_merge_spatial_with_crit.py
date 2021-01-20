#!python3


import argparse
import os
from collections import deque
import sys
from time import time

from termcolor import colored as col


my_parser = argparse.ArgumentParser(description='Script tha given a dataset merges the spatial data with the synopses.',
                                    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

my_parser.add_argument('dataset',
                       type=str,
                       choices=sorted([d for d in os.listdir(
                           '../../data') if os.path.isdir(os.path.join('../../data/', d))]),
                       help=col('The dataset to use.\n', 'cyan'))

my_parser.add_argument('--enriched', '-e',
                       action='store_true',
                       help=col('Whether to create an enriched dataset (add original noiseless AIS messages to ctitical).\n', 'cyan'))

args = my_parser.parse_args()
dataset = args.dataset
enriched = args.enriched


if enriched:
    fileCrit = f'tmp_RTEC/{dataset}_enriched_without_spatial.csv'
    fileFinal = f'tmp_RTEC/{dataset}_enriched_with_spatial.csv'
    fileSpatial = '../../spatial-processing/example/brest/results/spatial_events.csv'
    # fileSpatial = '../../spatial-processing/example/brest/results/spatial_events_enriched.csv'

else:
    fileCrit = f'tmp_RTEC/{dataset}_critical_without_spatial.csv'
    fileFinal = f'tmp_RTEC/{dataset}_critical_with_spatial.csv'
    fileSpatial = '../../spatial-processing/example/brest/results/spatial_events.csv'


areas = deque([])
for l in open(fileCrit):
    w = l.split('|')
    typ = w[0]
    if typ == 'gap_start':
        areas.append((int(w[1]), w[3], '', 'gap_start'))

proximities = deque([])

cur_t = time()

with open(fileSpatial) as spat:
    l = spat.readline().replace('\n', '')
    while l:
        w = l.split(',')
        if 'proximity' in l:
            idd1 = w[0]
            idd2 = w[3]
            t1 = int(w[2])
            t2 = int(w[1])
            proximities.append((t1, t2, idd1, idd2))
        else:
            idd = w[0]
            t = int(w[1])
            area = w[2]
            event = w[3]
            areas.append((t, idd, area, event))
        l = spat.readline().replace('\n', '')

print(f"Read spatial data in {time()-cur_t:.1f} seconds.")
cur_t = time()

areas = deque(sorted(areas))
proximities = deque(sorted(proximities))

print(f"Sorted spatial data in {time()-cur_t:.1f} seconds.")


cur_t = time()

# Remove unnecasary entersArea
last = {}
to_remove = set()
for i, (t, idd, area, event) in enumerate(areas):
    if event == 'gap_start':
        last[idd] = set()
    elif event == 'leavesArea':
        if idd in last and area in last[idd]:
            last[idd].remove(area)
    elif event == 'entersArea':
        if idd not in last:
            last[idd] = set()

        if area in last[idd]:
            to_remove.add(i)
        else:
            last[idd].add(area)
    else:
        raise RuntimeError('Wrong event.')

print(f'To remove {len(to_remove)}, total areas {len(areas)}')

areas = deque(
    [x for i, x in enumerate(areas) if i not in to_remove and x[3] != 'gap_start']
)
print(f'Final areas {len(areas)}')

print(f"Removed useless entersArea in {time()-cur_t:.1f} seconds.")


cur_t = time()

with open(fileFinal, 'w') as final, open(fileCrit) as crit:
    l = crit.readline()
    while l:
        w = l.split('|')
        if w[0] == 'coord':
            t = int(w[1])
            while len(proximities) > 0 and proximities[0][0] < t:
                p = proximities.popleft()
                final.write(f'proximity|{p[1]}|{p[0]}|{p[1]}|true|{p[2]}|{p[3]}\n')

            while len(areas) > 0 and areas[0][0] < t:
                a = areas.popleft()
                final.write(f'{a[3]}|{a[0]}|{a[0]}|{a[1]}|{a[2]}\n')

        final.write(l)
        l = crit.readline()

    while len(proximities) > 0:
        p = proximities.popleft()
        final.write(f'proximity|{p[1]}|{p[0]}|{p[1]}|true|{p[2]}|{p[3]}\n')

    while len(areas) > 0:
        a = areas.popleft()
        final.write(f'{a[3]}|{a[0]}|{a[0]}|{a[1]}|{a[2]}\n')

print(f"Made merged file in {time()-cur_t:.1f} seconds.")
