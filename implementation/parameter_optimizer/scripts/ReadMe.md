# Folder *scripts/*

#### This ReadMe provides info about the scripts in this folder.

These scripts work in python 3.7 and later (incompatibility with previous python3 versions arise due to the use of f-strings). In general these scripts require the following python3 packages: `deap`, `tqdm`, `matplotlib`, `numpy`, `termcolor`, `sklearn`(to a very small degree)

Some categorization can be done on the file name:

* Files starting with **r_** concern the incremental version of the genetic algorithm (which was originally called running GA, thus the r prefix).
* Files starting with **RTEC_** are used to create and edit files necessary for running RTEC.
* The rest of the files have no prefix.

From now on a brief overview of each file is given. For a more extensive summary, check the docstring of each file or the argparse description.


## Some general Notation

* The phrase "file code" is used for the name of the files in folder `../../data/{dataset}/data_per_type/cross/type{X}/`. Specifically if you see in the MarineTraffic dataset some "file codes" are month, march, april, etc.

---

### Libraries File

This section is for a single file `local_lib.py`. This file contains various auxiliary functions and variables:

* `SHIP_TYPES`, the mapping from type number to name.
* `PARAMETERS`, the name of the synopses parameters and the range to search from.
* `crit()`, the function that implements the optimization function.
* `estimate_RMSE()`, the function that estimates the rmse and ratio from the synopses.
* Class `Deamon`, which runs the Synopses Generator and returns the RMSE and Ratio. Because multiple instances of Deamon can run at once, each requires to use a different .jar for running the Synopses-Generator (why? send me an email, it will take too long to explain here). This requires each Deamon to have a separate id to know which jar to use. For this reason a file `tmp/ids.txt` is used that holds all the already used ids.

---

### Genetic Algorithms

This section is for the 3 files that run the GA.

* `genetic.py` Runs the simple genetic algorithm, i.e. on a static data set. The arguments, which also explains how to use script, are:
    - `-type` is an integer that denotes the ship type.
    - `-p` is an integer, the part to exclude (to make sense keep reading). First of all, each dataset is separated to parts (read the documentation in `../../data` for more explanations). Because all our experiments were for 6-fold cross validation, giving this argument e.g. the value 3 will have the GA train on parts 1,2,4,5,6. Then another script can do the validation on part 3. At some point the part numbers could be greater than 6, so this works for any **p**: For any **p**, find the interval **[6n+1, 6n+6]** that contains **p**, and train on parts **[6n+1, 6n+6]-{p}**.
    - `-opt` is an string that dictates what optimization function to use (see the 3rd argument in function `crit()` in file `local_lib.py`).
    - `-data` is a string, the dataset to use, i.e. the folder in `../../data`.
    - `-ngen` and `-pops` are the number of generations and population size for the GA. Both default to 15.
    - `fcode` the file-code to use, i.e. the name of the file: `../../data/{dataset}/data_per_type/cross/type{X}/{fcode}{part_number}.csv`. For more information see the documentation in `../../data`.

  This script saves the results in a .pkl file, in location `saves/{data}/type{type}/{fcode}{p}.pkl` (where inside the {}'s the corresponding arguments are used) as a 2-tuple: The first element contains a dictionary, mapping a list of synopses-parameters to a (RMSE,Ratio)-tuple (contains EVERY list of synopses-parameters that was valuated) and the second element contains information about running times.
  
  **Important:** If before running this script other results are stored in the .pkl file, then these results will be *used* to avoid a cold start, and then *updated* (and not overwritten) by the results of this script.

* `r_genetic.py` Runs the incremental genetic algorithm, i.e. it runs GA on a batch, then on 2 batches, then on 3 batches, etc. The arguments, which also explains how to use script, are:
    - `data` is a string, the dataset to use, i.e. the folder in `../../data`.
    - `type` is an integer that denotes the ship type.
    - `opt` is an string that dictates what optimization function to use (see the 3rd argument in function `crit()` in file `local_lib.py`).
    - `popsizes` is a comma separated list of integers (without spaces) that dictates the population size in each batch. If the list is smaller than the batches, then the last element of the list is used for the last batches.
    - `gennumbers` is a comma separated list of integers (without spaces) that dictates the number of generations in each batch. If the list is smaller than the batches, then the last element of the list is used for the last batches.
    - `--start_from` is an integer that dictates from which batch to start from. Defaults to 0, in which case the first generation of individuals is picked at random. If the value of this argument is greater i>0, then the script will try to recover the results of the i-1 batch to create the first generation of individuals for batch i. Basically this argument was used to avoid restarting the training from the first batch when unexpected errors occurred.

  This script saves the results in a .pkl file, in location `saves_running/{data}/type{type}/{fcode}.pkl`, where {fcode} is the batch used for training. E.g. if the training was on months March to May, the results will be stored in file `may.pkl`. Each file contains a 2-tuple: The first element contains a dictionary, mapping a list of synopses-parameters to a (RMSE,Ratio)-tuple (contains EVERY list of synopses-parameters that was valuated) and the second element contains a list of lists of individuals (the outer list indexes the generations, and the inner list indexes the individuals, e.g. if said list is `l`, then `l[1][2]` is the 2nd individual of the 1st generation (there is a 0th generation)).

  **Important:** Unlike `genetic.py` this script will *overwrite* previous results in .pkl files.
  **Also Important:** This should have been made differently, but to run `r_plotter.py` and get the plots, the stdout of this script should be redirected to file `logs/running_{dataset}_{ship_type}_t60_new.log`, from where `r_plotter.py` gets important info. To change this edit `r_plotter.py`.

* `hyperparam.py` This is an old file and I doubt its going to be useful. It might contain bugs. For the old optimization function (coded `new,x,y` in `local_lib.py`'s `crit()` function) it tries a combination of different values for the hyper-parameters and trains the GA. The results are shown using `bounds.py`.

---

### Evaluating files for the Genetic Algorithms

This section is for the files that use the GA's results and evaluate on new (unseen) data.

* `valuate.py` Runs the evaluation of the training of `genetic.py`. It is a fairly simple script that goes to the results .pkl file created by `genetic.py` and for the best individual there stores its `(RMSE, Ratio)` to another .pkl file (does not overwrite previous results). Note that if the training file was `june3.pkl`, the valuation results will be in `eval_june3.pkl`.
* `runner.py` Can and should be used to run `genetic.py` and `valuate.py` in succession. Stores the stdout of the scripts in the `logs` folder. For more information read the comments in this script.

* `r_eval.py` Runs the evaluation of the training of `r_genetic.py`. It is a fairly simple script that goes to the results .pkl files created by `r_genetic.py` and for the best individual in each training there stores its `(RMSE, Ratio)` to other .pkl files (does not overwrite previous results).

---

### Plotting/Outputting Files

These files simply take various outputs and plots or shows them.

* `best.py` Finds the parameters that minimized an optimization function, over the 6 folds.
* `bounds.py` Finds the hyper-parameter values for which RMSE and Ratio Bounds hold (old technique see MBDW paper).
* `plotter.py` Plots the results of the 6-fold cross validation. It does not perform any experiments.
* `r_plotter.py` Plots the progress of the incremental GA on the training set (i.e. the score of the best individual in each generation of each batch).
* `r_plot_eval.py` Plots the evaluation results of the incremental GA for each batch, i.e. for the batch of march-may shows the performance of the best individual (based on march-may) on june.

---

### Scripts for RTEC

These scripts are for creating files for RTEC. The order of the scripts is the order they should be run. Note that these experiments have been done only on the Brest dataset, thus these scripts only work for the Brest dataset. With minor tweaks they could run on the MarineTraffic dataset. Also note that these scripts require huge amounts of RAM, so they probably can be run only on obelix (they definitely crash on my 16GB machine).

* `RTEC_run_optimal_synopses.py` Runs the synopses for *all* the types in brest. Uses files in `../../data/brest/data_per_type/all/` (if they not exist error occurs). Creates and stores results in folder `./tmp_RTEC`. The parameters used for the synopses are either the default (see the script's arguments) or those in variable `OPT_BREST_PARAMS` in `local_lib.py`.

* `RTEC_relabel.py` Relabels the critical points of synopses-output files according to some parameter values.

* `RTEC_make_prespatial.py` This scripts creates the files requires to run the spatial analysis and also the files that will be merged with the spatial results.

* `RTEC_merge_spatial_with_crit.py` This scripts merges the data produced by the `RTEC_make_prespatial.py` script (more specifically the files ending in `without_spatial.csv`) with the spatial data. The spatial data, for the brest dataset, are stored in `/implementation/spatial-processing/example/brest/results/spatial_events.csv` - in that folder there already exists compressed files with spatial data for the default parameters and for the parameters created by running the GA with a threshold of 15m.

---

### MISC.

* `worker.py` A simple script that runs sequentially commands. These commands are read from file `runs.info`. Note that multiple `worker.py`s can be run simultaneously.