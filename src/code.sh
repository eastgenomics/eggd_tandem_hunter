#!/bin/bash

# Runs TandemHunter to produce individual comparison_csv files with PTD predictions
# Also generates single .xlsx spreadsheet with PTD predictions for query
# per_target_coverage files


# -e = exit on error; -x = output each line that is executed to log; -o pipefail = throw an error if there's an error in pipeline
set -e -x -o pipefail

# Make directories to hold outputs
mkdir /home/dnanexus/out
mkdir /home/dnanexus/out/summary_csvs
mkdir /home/dnanexus/out/summary_xlsx

# Download inputs from DNAnexus
dx-download-all-inputs

# run script for PTD prediction outputs
python3 /home/dnanexus/TandemHunter.py -B /home/dnanexus/in/coverage_files --intervals /home/dnanexus/in/intervals -O /home/dnanexus/out/summary_csvs $advanced_options

# Run second script (if number of files greater than 1)
# collate data into single dataframe
#if f in ["$coverage_targets_file"]>1 ; then
python3 generate_comparison_csv_to_xls.py --comparison_csv /home/dnanexus/out/summary_csvs $run

# Upload outputs (from /home/dnanexus/out) to DNAnexus
dx-upload-all-outputs --parallel