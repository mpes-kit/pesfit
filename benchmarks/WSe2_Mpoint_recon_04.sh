#!/bin/bash

## Reconstruct 4 valence bands of WSe2
NBAND=4
NSPEC=625
EOFS="0.10 0.14 0.18 0.22 0.26"
NWORK=4
CHUNKSIZE=100
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./02_WSe2_Mpoint.py"
FPATH="WSe2_Mpoint_recon_04.txt"
> $FPATH

# Tune the relative energy shift in initialization for 3rd band
echo "Tuning initial conditions for reconstructing band #3 ..."
for EOF in $EOFS
do
    SHFTS="0.20 0.16 $EOF 0"
    echo "total band = $NBAND, current band = 3, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="sequential" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 4th band
EOFS="0.10 0.14 0.18 0.22 0.26"
echo "Tuning initial conditions for reconstructing band #4 ..."
for EOF in $EOFS
do
    SHFTS="0.20 0.16 0.26 $EOF"
    echo "total band = $NBAND, current band = 4, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done