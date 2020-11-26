#!/bin/bash

NBAND=2
NSPEC=900
EOFS=0.0
SIZES="150 200"
FPATH="WSe2_Kpoint_benchmark.txt"
> $FPATH

# Run multiple fitting to find a better chunksize
for CS in $SIZES
do
    echo "total band = $NBAND, total spec = $NSPEC, chunk size = $CS" >> $FPATH
    /cygdrive/c/ProgramData/Anaconda3/python ./01_WSe2_Kpoint.py -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=4 -cs=$CS -ofs=$EOFS >> $FPATH
    echo "" >> $FPATH
done