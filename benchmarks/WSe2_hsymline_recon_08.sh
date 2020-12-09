#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=8
NSPEC=186
# EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
NWORK=50
CHUNKSIZE=5
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./03_WSe2_hsymline.py"
FPATH="WSe2_hsymline_recon_08.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

# Tune the relative energy shift in initialization for 5th band
EOFS="0.05 0.10 0.15 0.20 0.25 0.30"
echo "Tuning initial conditions for reconstructing band #5 ..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 5, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 6th band
EOFS="-0.10 -0.05 0.00 0.05 0.10 0.15 0.20"
echo "Tuning initial conditions for reconstructing band #6..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 $EOF 0 0"
    echo "total band = $NBAND, current band = 6, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 7th band
EOFS="-0.10 -0.05 0.00 0.05 0.10"
echo "Tuning initial conditions for reconstructing band #7..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 $EOF 0"
    echo "total band = $NBAND, current band = 7, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 8th band
EOFS="-0.10 -0.05 0.00 0.05 0.10"
echo "Tuning initial conditions for reconstructing band #8..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 $EOF"
    echo "total band = $NBAND, current band = 8, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done