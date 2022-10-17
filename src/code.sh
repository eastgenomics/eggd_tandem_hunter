#!/bin/bash

# Runs TandemHunter to produce individual comparison_csv files with PTD predictions
# Also generates single .xlsx spreadsheet with PTD predictions for query
# per_target_coverage files


# -e = exit on error; -x = output each line that is executed to log; -o pipefail = throw an error if there's an error in pipeline
set -e -x -o pipefail

# Install packages from the python asset
#pip3 install /pytz-*.whl /numpy-*.whl /pandas-*.whl
pip3 install pandas==1.1.3 #fix, should be installed from file
pip3 install openpyxl
# Make directories to hold outputs
mkdir /home/dnanexus/out
mkdir /home/dnanexus/out/comparison_csv
mkdir /home/dnanexus/out/comparison_xlsx

# Download inputs from DNAnexus in parallel, to go into /home/dnanexus/in/
echo "download_inputs"
dx-download-all-inputs --parallel
echo "download_complete"
ls /home/dnanexus/in/intervals/
# run script for PTD prediction outputs
echo "Tandemhunter_test"
echo "test_complete"
python3 TandemHunter.py -B /home/dnanexus/in/coverage_files/ --intervals /home/dnanexus/in/intervals/* -O /home/dnanexus/out/comparison_csv $advanced_options
echo "tandemhunter_done"
# Run second script (if number of files greater than 1)
# collate data into single dataframe
python3 generate_comparison_csv_to_xls.py --comparison_csv /home/dnanexus/out/comparison_csv/*.pertarget_.cvg_comparison.csv $run
mv *comparison_csv.xlsx /home/dnanexus/out/comparison_xlsx
# Upload outputs (from /home/dnanexus/out) to DNAnexus
dx-upload-all-outputs --parallel