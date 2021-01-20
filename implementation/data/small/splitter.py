#!/usr/bin/python3


import datetime
import os


first = True
d = {}
final = {}

for l in open('ais.csv'):
    w = l.split(',')

    if first:
        first = False
        for i in range(len(w)):
            d[w[i]] = i
        continue

    idd = w[d['shipid']]
    lon = w[d['lon']]
    lat = w[d['lat']]
    t = int(1000*datetime.datetime.strptime(w[d['t']], '%Y-%m-%dT%H:%M:%SZ').timestamp())
    head = w[d['heading']]
    course = w[d['course']]
    speed = w[d['speed']]
    typ = int(w[d['shiptype']]) if w[d['shiptype']] != '' else 90
    if 40 <= typ <= 49:
        typ = 40
    elif 60 <= typ <= 69:
        typ = 60
    elif 70 <= typ <= 79:
        typ = 70
    elif 80 <= typ <= 89:
        typ = 80
    elif 90 <= typ <= 99:
        typ = 90

    if typ not in final:
        final[typ] = []

    final[typ].append((
        t,
        f'{t} {idd} {lon} {lat} {head} {course} {speed} 0'
    ))


try:
    os.makedirs(f'data_per_type/all/')
except:
    pass

for typ, points in final.items():

    print(f'type {typ} has {len(points)} lines')

    with open(f'data_per_type/all/type_{typ}.csv', 'w') as f:
        for t, s in sorted(points):

            f.write(s)
            f.write('\n')
