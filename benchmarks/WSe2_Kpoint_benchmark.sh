#!/bin/bash

NBAND=2
NSPEC=900
SIZES="5 10 50 150 200"
FPATH="WSe2_Kpoint_benchmark.txt"

# Run multiple fitting to find a better chunksize
for CS in $SIZES
do
    echo "total band = $NBAND, total spec = $NSPEC, chunk size = $CS" >> FPATH
    python3 ./01_WSe2_Kpoint.py -nb=NBAND -ns=NSPEC -op="parallel" -bk="parmap" -nw=4 -cs=CS >> FPATH
    echo "" >> FPATH
done