"""
script to generate .xls file from a run of cvg_comparison.csv generated from TandemHunter

"""

import argparse
from pathlib import Path
import pty
import subprocess
import os
import sys
import pytest

import pandas as pd

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--comparison_csv', type=argparse.FileType('r'), nargs="+", required=True,
        help='all cvg_comparison.csv files to generate .xls report for tandemhunter output'#better if give input directory
    )
    parser.add_argument(
        '--run',
        help='name of run to prefix output .xls file with'
    )

    args = parser.parse_args()
    #print(args)
    #print(args.comparison_csv)

    return args

def generate_PTD_KMT2A_df(args):
    """Generates dataframe from multiple per cvg_comparison.csv from tandemhunter

    Returns:
    -PTD_KMT2A(df):df of normalized coverages for KMT2A exons 3 and 27, fold coverage difference
    between exons and algorithm predictions for PTDs in KMT2A (as either true/false)
    """
    #create empty list for dataframes
    all_data = []
    for index, file in enumerate(args.comparison_csv):
        df = pd.read_csv(file.name, delimiter=',')
    #for index,file in enumerate(args.comparison_csv):
    #    if index == 0:
    #        df = pd.read_csv(file.name, delimiter=',')
    #    else:
    #        df = pd.read_csv(file.name, delimiter=',') # , header=None, skiprows=[0])
        #df = pd.concat(map(pd.read_csv, file.name), ignore_index=True)
        #print(index)='[.]
        #print(df)
        all_data.append(df)
    #print(all_data)
    merged_data = pd.concat(all_data)
    print(merged_data)

    #check df has no duplicate results
    assert merged_data['sample_id'].is_unique, 'df has duplicate sample results'

    return merged_data


def KM2TA_df_to_xls(PTD_KM2TA_1):
   """"Generates .xls spreadsheet with PTD predictions from TandemHunter

   Returns:
   .xls file with fold coverage differences for normalized coverage for exons 3 and 27 of
   KM2TA gene and TRUE/FALSE statement to suggest if sample likely has PTDs
   """

   #print(PTD_KM2TA_1.dtypes)
   #convert boolean to string to keep true/false
   PTD_KM2TA_1['above_cut_off'] = PTD_KM2TA_1['above_cut_off'].astype('str')
   PTD_KM2TA_1.to_excel("comparison_csv.xlsx", index = False, header = True)


def main():
   args = parse_args()
   PTD_KM2TA_1 = generate_PTD_KMT2A_df(args)

   #write output bed file
   KM2TA_df_to_xls(PTD_KM2TA_1)


if __name__ == "__main__":
   main()