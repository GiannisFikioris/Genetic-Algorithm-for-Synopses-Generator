#!/usr/bin/python3


import os
import sys


mvn = 'mvn package -Pbuild-jar'


inp = 'src/main/scala/eu/datacron/synopses/maritime/TrajectoryStreamManager.scala'
old_jar = 'target/datacron_trajectory_synopses-0.7.jar'
jar = 'target/datacron_trajectory_synopses-0.7'

if not os.path.exists('target/'):
    os.mkdir('target/')


for x in os.listdir('target/'):
    if x[-4:] == '.jar':
        os.remove('target/' + x)

with open(inp, 'r') as f:
    og = f.read()

try:
    for m in range(10 if len(sys.argv) == 1 else int(sys.argv[1])):
        m = str(m)
        new = og.replace('tmp/maritime_config.properties',
                         'tmp/maritime_config{}.properties'.format(m))
        with open(inp, 'w') as f:
            f.write(new)
        os.system(mvn)
        new_jar = jar + '-type'+m+'.jar'
        os.rename(old_jar, new_jar)

finally:
    with open(inp, 'w') as f:
        f.write(og)
        os.system(mvn)
