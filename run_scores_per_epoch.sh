#!/bin/bash

# activate the proper conda environment
export PYTHONIOENCODING=utf-8
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
echo "Computing scores for $MODEL_FILE..."

# move the default model file to a temporary directory
mv "$MODEL_FILE" "$MODEL_FILE.bak"
echo "Saving $MODEL_FILE to $MODEL_FILE.bak..."

# determine to which file to write
OUTPUT_FILE="${MODEL_FILE%.*}.scores"
echo "Writing scores to $OUTPUT_FILE..."

# run the computation once for each model
MODEL_BASENAME="${MODEL_FILE%.*}_"
MODEL_BASENAME_LEN=$(expr 1 + ${#MODEL_BASENAME})
MODEL_AT_EPOCH=`ls -1 $MODEL_BASENAME*.model | sort -n -k "1.${MODEL_BASENAME_LEN}"`
for model in $MODEL_AT_EPOCH; do
  mv "$model" "$MODEL_FILE"
  echo "Select model $model..."
  python nmt_translate.py >> $OUTPUT_FILE
  mv "$MODEL_FILE" "$model"
done

# move the default model file back
mv "$MODEL_FILE.bak" "$MODEL_FILE"
echo "Restore $MODEL_FILE.bak to $MODEL_FILE..."
