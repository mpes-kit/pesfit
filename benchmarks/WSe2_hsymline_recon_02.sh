#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=2
NSPEC=186
# EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
NWORK=4
CHUNKSIZE=30
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./03_WSe2_hsymline.py"
FPATH="WSe2_hsymline_recon_02.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

# Tune the relative energy shift in initialization for 1st band
EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
echo "Tuning initial conditions for reconstructing band #1 ..."
for EOF in $EOFS
do
    SHFTS="$EOF 0"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

EOFS="0.36 0.38 0.42"
echo "Tuning initial conditions for reconstructing band #1 ..."
for EOF in $EOFS
do
    SHFTS="$EOF 0"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 2nd band
EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
echo "Tuning initial conditions for reconstructing band #2..."
for EOF in $EOFS
do
    SHFTS="0.40 $EOF"
    echo "total band = $NBAND, current band = 2, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done