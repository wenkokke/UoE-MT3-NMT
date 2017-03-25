#!/bin/bash

# activate the proper conda environment
source activate mtenv

# capture the model filename from nmt_config
MODEL_FILE=`python <<EOF
# coding: utf-8
import os
import sys
devnull = open(os.devnull, 'w')
old_stdout = sys.stdout
sys.stdout = devnull
from nmt_config import *
sys.stdout = old_stdout
print(model_fil)
EOF`

# move the default model file to a temporary directory
TMPDIR=`mktemp -d 2>/dev/null || mktemp -d -t 'MT3'`
mv "$MODEL_FILE" "$TMPDIR/$(basename $MODEL_FILE)"

# run the computation once for each model
MODEL_BASENAME="${MODEL_FILE%.*}"
for model_at_epoch in "$MODEL_BASENAME*.model"; do
    echo "$model_at_epoch"
    ln -s "$model_at_epoch" "$MODEL_FILE"
    python <<EOF
# coding: utf-8
from nmt_translate import *
main()
compute_dev_bleu()
compute_dev_pplx()
EOF
    unlink "$MODEL_FILE"
done

# move the default model file back
mv "$TMPDIR/$(basename $MODEL_FILE)" "$MODEL_FILE"
