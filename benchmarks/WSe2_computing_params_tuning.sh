#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=2
NSPEC=900
# EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
NWORKERS="4 10 20 40 60 80 100 120"
CHUNKSIZES="4 8 16 32 64 128 256 512"
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_tuning_02.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

# Tune the relative energy shift in initialization for 1st band
SHFTS="0.26 0.26"
for CS in $CHUNKSIZES
do
    for NWORK in $NWORKERS
    do
        echo "Tuning computing resource settings: $NWORK worker(s), with $CS tasks each ..."
        echo "total band = $NBAND, total spec = $NSPEC, worker = $NWORK, chunk size = $CS, energy shift = $SHFTS" >> $FPATH
        $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CS -ofs $SHFTS -varin="theory" >> $FPATH
        echo "" >> $FPATH
    done
done