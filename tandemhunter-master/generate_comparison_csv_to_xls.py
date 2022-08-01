"""
script to generate .xls file from a run of cvg_comparison.csv generated from TandemHunter

"""

import argparse
from ast import Break
from pathlib import Path
from pickle import TRUE
import pty
import subprocess
import os
import sys

import pandas as pd

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--comparison_csv', type=argparse.FileType('r'), nargs="+", required=TRUE,
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
    # read in intervals from first per targets coverage files
    # and add to coverage_ratio_df
    PTD_KM2TA_df = pd.read_csv(
        args.comparison_csv[0], delimiter=',', header=0
    )
    print(PTD_KM2TA_df)
    #print(type(PTD_KM2TA_df))
    # read all files in and add to coverage_ratio_df but ignore header row
    #add this to PTD_KM2TA_df
    #need to exclude first file though
    for file in args.comparison_csv:
        KMT2A_dfs =pd.read_csv()
        PTD_KM2TA_1 = pd.concat[[KMT2A_dfs, PTD_KM2TA_df]]
        print(PTD_KM2TA_1)
            #lines = fh.readlines()[1:]#.Skip(1).FirstOrDefault()
            #PTD_KM2TA_df = append(lines, )
            #print(type(lines))
            #print(lines)
    #print(PTD_KM2TA_df)


    #put tandemhunter output into df
    #file_df = pd.read_csv(
    #   file.name, delimiter=',', header=0)
    #file_df = pd.DataFrame(lines)

    #join data frames
    #file_df = PTD_KM2TA_df

    #check to ensure no duplicates
    #assert

    return PTD_KM2TA_1

def KM2TA_df_to_xls(PTD_KM2TA_1):
   """"Generates .xls spreadsheet with PTD predictions from TandemHunter

   Returns:
   .xls file with fold coverage differences for normalized coverage for exons 3 and 27 of
   KM2TA gene and TRUE/FALSE statement to suggest if sample likely has PTDs
   """
   PTD_KM2TA_1.to_excel()

def main():
   args = parse_args()
   PTD_KM2TA_1 = generate_PTD_KMT2A_df(args)

    #write output bed file
   KM2TA_df_to_xls(PTD_KM2TA_1, args.run)


if __name__ == "__main__":
   main()