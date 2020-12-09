#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NBAND=14
NSPEC=186
# EOFS="0.30 0.35 0.40 0.45 0.50 0.55"
NWORK=80
CHUNKSIZE=3
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./03_WSe2_hsymline.py"
FPATH="WSe2_hsymline_recon_14.txt"
> $FPATH # Will wipe the previous namesake txt file if it exists

# Tune the relative energy shift in initialization for 9th band
EOFS="0.10 0.15 0.20 0.25 0.30"
echo "Tuning initial conditions for reconstructing band #9 ..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 $EOF 0 0 0 0 0"
    echo "total band = $NBAND, current band = 9, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 10th band
EOFS="0.10 0.15 0.20 0.25 0.30"
echo "Tuning initial conditions for reconstructing band #10..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 0.2 $EOF 0 0 0 0"
    echo "total band = $NBAND, current band = 10, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 11th band
EOFS="0.10 0.15 0.20 0.25 0.30"
echo "Tuning initial conditions for reconstructing band #11..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 0.2 0.25 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 11, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 12th band
EOFS="0.05 0.10 0.15 0.20 0.25 0.30 0.35"
echo "Tuning initial conditions for reconstructing band #12..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 0.2 0.25 0.25 $EOF 0 0"
    echo "total band = $NBAND, current band = 12, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 13th band
EOFS="0.15 0.20 0.25 0.30 0.35"
echo "Tuning initial conditions for reconstructing band #13..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 0.2 0.25 0.25 0.30 $EOF 0"
    echo "total band = $NBAND, current band = 13, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 14th band
EOFS="-0.05 0.0 0.05 0.10 0.15"
echo "Tuning initial conditions for reconstructing band #14..."
for EOF in $EOFS
do
    SHFTS="0.40 0.35 0.25 0.05 0.1 -0.05 0.05 -0.05 0.2 0.25 0.25 0.30 0.30 $EOF"
    echo "total band = $NBAND, current band = 14, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done