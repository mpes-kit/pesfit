#!/bin/bash

## Reconstruct 14 valence bands of WSe2
NBAND=14
NSPEC=900
EOFS="0.22 0.26 0.30 0.34 0.38"
NWORK=50
CHUNKSIZES=30
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_recon_14.txt"
> $FPATH

# Tune the relative energy shift in initialization for 9th band
echo "Tuning initial conditions for reconstructing band #9 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 9, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 10th band
echo "Tuning initial conditions for reconstructing band #10 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 10, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 11th band
echo "Tuning initial conditions for reconstructing band #11 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 7, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 12th band
echo "Tuning initial conditions for reconstructing band #12 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 8, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done $FPATH
done

# Tune the relative energy shift in initialization for 13th band
echo "Tuning initial conditions for reconstructing band #13 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 7, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

# Tune the relative energy shift in initialization for 14th band
echo "Tuning initial conditions for reconstructing band #14 ..."
for EOF in $EOFS
do
    SHFTS="0.26 0.26 0.26 0.2 $EOF 0 0 0"
    echo "total band = $NBAND, current band = 8, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='LDA_synth_14' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done $FPATH
done