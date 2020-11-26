#!/bin/bash

## 8 valence bands of WSe2
NBAND=8
NSPEC=900
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=50
CHUNKSIZES=30
FPATH="WSe2_Kpoint_recon_8.txt"
> $FPATH

# Tune the relative energy shift in initialization for optimizing reconstruction outcome (4 bands)
for CS in $CHUNKSIZES
do
    echo "total band = $NBAND, total spec = $NSPEC, chunk size = $CS" >> $FPATH
    /cygdrive/c/ProgramData/Anaconda3/python ./01_WSe2_Kpoint.py -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CS -ofs=$EOFS >> $FPATH
    echo "" >> $FPATH
done