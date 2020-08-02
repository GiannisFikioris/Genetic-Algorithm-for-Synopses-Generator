# Folder *scripts/*

#### This ReadMe provides info about the scripts in this folder.

These scripts work in python 3.7 and later (incompatibility with previous python3 versions arise due to the use of f-strings). In general these scripts require the following python3 packages: ```deap```, ```tqdm```, ```matplotlib```, ```numpy```, ```termcolor```

Some categorization can be done on the file name:

* Files starting with **r_** concern the incremental version of the genetic algorithm (which was originally called running GA, thus the r prefix).
* Files starting with **RTEC_** are used to create and edit files necessary for running RTEC.
* The rest of the files have no prefix.

From now on a brief overview of each file is given. For a more extensive summary, check the docstring of each file or the argparse description.


## Some general Notation

* The phrase "file code" is used for the name of the files in folder ```../../data/{dataset}/data_per_type/cross/type{X}/```. Specifically if you see in the MarineTraffic dataset some "file codes" are month, march, april, etc.
