#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=4
NSPEC=186
# EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
NWORK=10
CHUNKSIZE=50
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./03_WSe2_hsymline.py"
FPATH="WSe2_hsymline_recon_04.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

# Tune the relative energy shift in initialization for 3rd band
EOFS="0.20 0.25 0.30 0.35 0.40 0.45 0.50 0.55"
echo "Tuning initial conditions for reconstructing band #3 ..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 $EOF 0"
    echo "total band = $NBAND, current band = 3, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 4th band
EOFS="0.00 0.05 0.10 0.15 0.20 0.25 0.30"
echo "Tuning initial conditions for reconstructing band #4..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 $EOF"
    echo "total band = $NBAND, current band = 4, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done