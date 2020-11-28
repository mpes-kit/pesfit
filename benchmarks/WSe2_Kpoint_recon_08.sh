#!/bin/bash

## Reconstruct 8 valence bands of WSe2
NBAND=8
NSPEC=900
EOFS="0.32 0.36 0.40 0.44 0.48"
NWORK=40
CHUNKSIZE=30
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_recon_08.txt"
> $FPATH

# Tune the relative energy shift in initialization for 5th band
echo "Tuning initial conditions for reconstructing band #5 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 5, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 6th band
echo "Tuning initial conditions for reconstructing band #6 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 $EOF 0 0"
    echo "total band = $NBAND, current band = 6, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 7th band
echo "Tuning initial conditions for reconstructing band #7 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 0 $EOF 0"
    echo "total band = $NBAND, current band = 7, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 8th band
echo "Tuning initial conditions for reconstructing band #8 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 0 0 $EOF"
    echo "total band = $NBAND, current band = 8, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done