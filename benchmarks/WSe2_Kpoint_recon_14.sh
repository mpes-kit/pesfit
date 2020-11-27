#!/bin/bash

## Reconstruct 14 valence bands of WSe2
NBAND=14
NSPEC=900
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=50
CHUNKSIZES=30
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_recon_14.txt"
> $FPATH

# Tune the relative energy shift in initialization for optimizing reconstruction outcome (14 bands)
for CS in $CHUNKSIZES
do
    echo "total band = $NBAND, total spec = $NSPEC, worker = $NWORK, chunk size = $CS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CS -ofs=$EOFS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done