## This ReadMe provides info about the scripts in this folder.

These scripts work in python 3.7 and later (incompatibility with previous python3 versions will arise in some scripts due to the use of f-strings). In general these scripts require the following python3 packages: ```deap```, ```tqdm```, ```matplotlib```, ```numpy```, ```termcolor```

Files starting with **r_** concern the incremental version of the genetic algorithm (which was originally called running Genetic Algorithm, thus the r prefix).

From now on a brief overview of the primary files is given. For a more extensive summary, check the docstring of each file or the argparse description.


### Important Files

The 3 most important files are:

* ```local_lib.py```. This file contains some general functions and classes that are essential to running the algorithm. Should be able to be used as a black box.
* ```genetic.py```. This scripts runs the simple genetic algorithm (not the incremental one). For more information about this script see the argparse description. (need Flink to be running in the background).
* ```r_genetic.py```. This scripts runs the incremental genetic algorithm. For more information about this script see the argparse description. (need Flink to be running in the background).

**Note:** Before running any of the two genetic algorithms read the file ```trajectory_synopses/ReadMe.md```.