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
mv "$MODEL_FILE" "$MODEL_FILE.bak"

# run the computation once for each model
MODEL_BASENAME="${MODEL_FILE%.*}"
for model_at_epoch in $MODEL_BASENAME*.model; do
    echo "$model_at_epoch"
    ln -s "$model_at_epoch" "$MODEL_FILE"
    python <<EOF
# coding: utf-8
from nmt_translate import *
main()
compute_dev_bleu()
compute_dev_pplx()
EOF
    rm "$MODEL_FILE"
done

# move the default model file back
mv "$MODEL_FILE.bak" "$MODEL_FILE"
