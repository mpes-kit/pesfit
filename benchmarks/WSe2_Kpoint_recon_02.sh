#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=2
NSPEC=900
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=4
CHUNKSIZE=300
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_recon_02.txt"
> $FPATH

# Tune the relative energy shift in initialization for 1st band
echo "Tuning initial conditions for reconstructing band #1 ..."
for EOF in $EOFS
do
    SHFTS="$EOF 0"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 2nd band
echo "Tuning initial conditions for reconstructing band #2..."
for EOF in $EOFS
do
    SHFTS="0.26 $EOF"
    echo "total band = $NBAND, current band = 2, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done