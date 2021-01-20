#!/bin/python3


import csv
import os


types = {}
finals = {}
with open('nari_static.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        typ = row['shiptype']
        if len(typ) > 0:
            typ = int(typ)
        else:
            typ = 0
        types[row['sourcemmsi']] = typ
        finals[typ] = []

with open('nari_dynamic.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        idd = row['sourcemmsi']
        t = row['t']
        lon = row['lon']
        lat = row['lat']

        typ = types.get(idd, 0)

        finals[typ].append((
            int(t),
            f"{t}000 {idd} {lon} {lat} 0 0 0 0"
        ))

if not os.path.exists('data_per_type/all'):
    os.mkdir('data_per_type/all')

for k, v in finals.items():
    v.sort()
    if len(v) > 0:
        print(k, len(v))
        with open(f'data_per_type/all/type_{k}.csv', 'w') as f:
            for t, s in v:
                f.write(s)
                f.write('\n')
