#!/bin/bash

## Reconstruct 2 valence bands of WSe2
NSPEC=100
EOFS="0.25 0.30 0.40"
PYTHONPATH="/cygdrive/c/ProgramData/Anaconda3/python"
CODEPATH="./01_WSe2_Kpoint.py"
FPATH="WSe2_Kpoint_scaling_benchmark.txt"
> $FPATH

# Tune the relative energy shift in initialization for 1st band
NBAND=2
CHUNKSIZE=100
NWORK=4
echo "Spectrum fitting with components #1-2 ..."
for EOF in $EOFS
do
    SHFTS="$EOF $EOF"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

echo "Spectrum fitting with components #1-4 ..."
NBAND=4
CHUNKSIZE=50
NWORK=4
for EOF in $EOFS
do
    SHFTS="$EOF $EOF $EOF $EOF"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

echo "Spectrum fitting with components #1-8 ..."
NBAND=8
CHUNKSIZE=30
NWORK=4
for EOF in $EOFS
do
    SHFTS="$EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

echo "Spectrum fitting with components #1-12 ..."
NBAND=12
CHUNKSIZE=30
NWORK=4
for EOF in $EOFS
do
    SHFTS="$EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done

echo "Spectrum fitting with components #1-14 ..."
NBAND=14
CHUNKSIZE=30
NWORK=4
for EOF in $EOFS
do
    SHFTS="$EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF $EOF"
    echo "total band = $NBAND, current band = 1, total spec = $NSPEC, worker = $NWORK, chunk size = $CHUNKSIZE, energy shift = $SHFTS" >> $FPATH
    $PYTHONPATH $CODEPATH -nb=$NBAND -ns=$NSPEC -op="parallel" -ds='symmetrized' -bk="async" -nw=$NWORK -cs=$CHUNKSIZE -ofs $SHFTS -varin="theory" >> $FPATH
    echo "" >> $FPATH
done