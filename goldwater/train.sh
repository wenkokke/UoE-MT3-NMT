#!/bin/bash

ALPHA=${ALPHA:-0.5}
P_HASH=${P_HASH:-0.5}
OUT_DIR=${OUT_DIR:-"model"}

if [[ -n $2 ]]
then
    N=$2
else
    N=10000
fi

./segment --out_dir "$OUT_DIR" --train_path "data/text.fr" -n $N -a $ALPHA -p $P_HASH
