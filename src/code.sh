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

# handle when NO query coverage files provided
if [ -z "$coverage_file" ]; then
	touch /home/dnanexus/out/summary_csv/noQuerycoveragefileFound.summary_csv
else
    # Download inputs from DNAnexus
    dx-download-all-inputs

# run script for PTD prediction outputs
python TandemHunter.py $advanced_options "$output_name" "${coverage_file[@]}"
# collate data into single dataframe (if tools ran in batch mode)
if []

mv ~/"${comparison_csv_prefix}.pertarget_coverage.tsv" ~/out/summary_csvs/

# Upload outputs (from /home/dnanexus/out) to DNAnexus
dx-upload-all-outputs --parallel