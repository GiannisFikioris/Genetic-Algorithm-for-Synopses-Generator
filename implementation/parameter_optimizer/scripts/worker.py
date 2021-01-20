#!/usr/bin/python3

import os
import sys
from time import sleep


if sys.version_info[0] != 3 or sys.version_info[1] < 7:
    raise EnvironmentError('Must run Python >= 3.7')

while True:

    # Read all the commands to be run
    with open('runs.info') as f:
        lines = f.read().split('\n')

    # Erase empty lines
    while len(lines) > 0 and len(lines[0]) < 2:
        lines.pop(0)

    # If no commands areleft break
    if len(lines) == 0:
        break

    # Get the command to tun
    cmd = lines.pop(0)

    # Write to file the rest of the commands thet were not used
    with open('runs.info', 'w') as f:
        for i in range(len(lines)):
            f.write(lines[i])
            if i < len(lines) - 1:
                f.write('\n')

    # Print command that will be run
    print(cmd)

    # Run command
    os.system(cmd)

    # Wait for a while. This is done so that if the previous command took too little to run,
    # `runs.info` will not be simultaneously read by multiple instances of worker.py.
    sleep(3)
