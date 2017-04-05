#!/bin/bash
export PYTHONIOENCODING=utf-8
echo "Creating MCB datasets"
source activate mtenv
python create_mcb_data.py
echo "Finished creating MCB datasets"

