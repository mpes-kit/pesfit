#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=8
NSPEC=186
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=10
CHUNKSIZE=50
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./03_WSe2_hsymline.py"
FPATH="WSe2_hsymline_recon_08.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

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
echo "Tuning initial conditions for reconstructing band #6..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 $EOF 0 0"
    echo "total band = $NBAND, current band = 6, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 7th band
echo "Tuning initial conditions for reconstructing band #7..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 $EOF 0 0"
    echo "total band = $NBAND, current band = 7, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 8th band
echo "Tuning initial conditions for reconstructing band #8..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.1 0 $EOF 0 0"
    echo "total band = $NBAND, current band = 8, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done