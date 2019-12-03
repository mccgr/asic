#!/bin/bash
python3 $ASIC_DIR/get_asic_csv.py
Rscript $ASIC_DIR/process_asic_csv.R