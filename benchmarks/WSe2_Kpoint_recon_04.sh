#!/bin/bash

## Reconstruct 4 valence bands of WSe2
NBAND=4
NSPEC=900
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=4
CHUNKSIZE=100
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_recon_04.txt"
> $FPATH

# Tune the relative energy shift in initialization for 3rd band
echo "Tuning initial conditions for reconstructing band #3 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.22 $EOF 0"
    echo "total band = $NBAND, current band = 3, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 4th band
EOFS="0.02 0.06 0.1 0.14 0.18 0.22 0.26 0.30 0.34 0.38"
echo "Tuning initial conditions for reconstructing band #4 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.22 0.26 $EOF"
    echo "total band = $NBAND, current band = 4, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done