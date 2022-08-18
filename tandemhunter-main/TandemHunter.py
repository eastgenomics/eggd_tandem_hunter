# Tandem Hunter: Identification of duplicated/amplified
# regions based on the comparison
# of normalise coverage between two intervals in given coverage file
# (PER_TARGET_COVERAGE from Picard CollectHsMetrics).

# Author: Helena L. Spiewak
# Contributors: Nadia Mohammed
# Date created: 2021-04-06
# Date modified: 2021-04-06

# It is used to identify KMT2A/MLL partial tandem duplications and is based on
# the method described by McKerrell et al., 2016, where they compare
# the coverage of exon 3 and exon 27 of MLL/KMT2A.

import pandas as pd
import numpy as np
import argparse
import sys
import os
import json
import multiprocessing as mp
import fnmatch
import functools
from datetime import datetime
import glob

# define Picard CollectHsMetrics PER_TARGET_COVERAGE columns
COV_COLUMN_DTYPES = {
    "chrom": "category",
    "start": "int",
    "end": "int",
    "length": "int",
    "name": "category",
    "%gc": "float64",
    "mean_coverage": "float64",
    "normalized_coverage": "float64",
    "min_normalized_coverage": "float64",
    "max_normalized_coverage": "float64",
    "min_coverage": "int",
    "max_coverage": "int",
    "pct_0x": "float64",
    "read_count": "int",
}


def tdh_argument_parser(args):
    """ Parse arguments for Tandem Hunter. """
    parser = argparse.ArgumentParser(
        description=(
            "Tandem Hunter: Identification of duplicated/amplified regions"
            "based on comparing normalised coverage between two intervals"
        )
    )
    required = parser.add_argument_group("required named arguments")
    required.add_argument(
        "-F", "--file", default=False, help="Path to coverage file OR"
    )
    required.add_argument(
        "-B",
        "--batch",
        default=False,
        help="Path to coverage files folder. DON'T use -F and -B together.",
    )
    required.add_argument(
        "--intervals",
        type=str,
        required=True,
        help=(
            "Path to json file containing intervals to compare coverage at."
            " These regions have to be in the coverage file as is as this "
            " programme uses pattern matching"
        ),
    )
    parser.add_argument(
        "--dup-threshold",
        type=float,
        default=1.122995,
        help="Default threshold for dup/amp regions if not in interval file",
    )
    parser.add_argument(
        "-O", "--out_dir",
        default=".", help="Output write directory"
    )
    parser.add_argument(
        "--out-fname-suffix",
        default=".cvg_comparison.csv",
        help="Filename suffix to use when naming results file",
    )
    parser.add_argument(
        "--processes", default=0,
        help="Number of processes to run in parallel",
    )
    parser.add_argument(
        "--cov-file-pattern",
        default="coverage.tsv",
        help="Filename suffix used to identify coverage files in batch mode",
    )
    parser.add_argument(
        "--metric",
        default="normalized_coverage",
        help="Metric to used in comparison",
    )
    parser.add_argument("--version",
        action="version", 
        version="%(prog)s 2.0.0")

    return parser.parse_args(args)


class TDHunter(object):
    """ Object containg methods that compare normalised coverage
        at two given intervals.
        :param: file: Path to coverage file
        :param: batch: Path to folder with a batch of coverage files
        :param: intervals: Path to file with intervals to compare coverage at
        :param: dup_threshold: Threshold used to identify dup/amp regions
        :param: out_dir: Output write directory
        :param: out_fname_suffix: Filename suffix for naming results file
        :param: processes: Maximum number of processes to run (default is cpu
                            count)
        :param: cov_file_pattern: Filename suffix to identify coverage files
                                    when in batch mode
        :param: column_dtypes: Dictionary with column name and datatype for
                            the given coverage file type
        :param: metric: Metric to used in comparison
        :returns: Writes a coverage comparison between two intervals to a text
                    file on per-sample basis
    """
    def __init__(
        self,
        file=False,
        batch=False,
        intervals=False,
        dup_threshold=1.122995,
        out_dir=".",
        out_fname_suffix=".cvg_comparison.csv",
        processes=0,
        cov_file_pattern=".qc.coverage.txt",
        column_dtypes=COV_COLUMN_DTYPES,
        metric="normalized_coverage",
    ):

        # store arguments
        try:
            self.file = os.path.abspath(file)
        except Exception:
            self.file = file
        try:
            self.batch = os.path.abspath(batch)
        except Exception:
            self.batch = batch
        try:
            self.intervals = os.path.abspath(intervals)
        except Exception:
            self.intervals = intervals
        self.dup_threshold = dup_threshold
        self.out_dir = os.path.abspath(out_dir)
        self.out_fname_suffix = out_fname_suffix
        self.processes = processes
        # use max cpu count available as number of processes if value not given
        if self.processes == 0:
            self.processes = mp.cpu_count()
        self.cov_file_pattern = cov_file_pattern
        self.column_dtypes = column_dtypes
        self.metric = metric

        # process a single file
        if self.file:
            # check and process the file
            self._process_file(
                file=self.file, intervals=self.intervals, out_dir=self.out_dir
            )

        # process a batch of files
        elif self.batch:
            # find the coverage files
            files = self._find_coverage_files(
                batch_dir=batch, cov_file_pattern=self.cov_file_pattern
            )
            # process the files in paralllel
            pool = mp.Pool(self.processes)
            # instance of class is passed to map (uses __call__
            # to call _process_file) for compatibility with python2.7
            results = pool.map(self, [file for file in files])
            pool.close()

        # print error if neither file or batch given
        else:
            sys.stderr.write(
                "[{0}] Error: File or batch folder not specified!".format(
                    datetime.now()
                )
            )
            sys.exit()

    @classmethod
    def _find_coverage_files(cls, batch_dir, cov_file_pattern):
        """ Method to find coverage files in a directory.
        :param: batch_dir: Path to batch directory
        :param: cov_file_pattern: Filename suffix to identify coverage files
        :returns: A list of coverage files found in given directory
        """
        print(
            "[{0}] Finding coverage files in {1}".format(
                datetime.now(), batch_dir
            )
        )

        try:
            coverage_files = glob.glob(
                os.path.join(batch_dir, "**", "*{0}".format(cov_file_pattern)),
                recursive=True,
            )
        # handle when glob recursive not available in older python versions
        except TypeError:
            coverage_files = []
            for root, dirnames, filenames in os.walk(batch_dir):
                for filename in fnmatch.filter(
                        filenames, "*{0}".format(cov_file_pattern)):
                    coverage_files.append(os.path.join(root, filename))
        except Exception as e:
            coverage_files = []
        return coverage_files

    @classmethod
    def _import_coverage(cls, file, column_dtypes, sep="\t"):
        """ Method to read output file from coverage file into a dataframe.
        :param: file: Path to coverage file
        :param: column_dtypes: Dictionary with column name and datatype for
                            the given coverage file type
        :param: sep: seperate used in coverage file (default is tab)
        :returns: reader iterable containing Pandas dataframe.
        """
        reader = pd.read_csv(
            file,
            sep=sep,
            header=0,
            skipinitialspace=True,
            na_values="-",
            dtype=column_dtypes,
            chunksize=10000,
        )

        return reader

    @classmethod
    def _import_intervals(cls, intervals, dup_threshold):
        """ Method to process interval json file and store as a dictionary
        :param: file: Path to interval json
        :param: dup_threshold: Threshold used to identify dup/amp regions
        :returns: Dictionary
        """
        # open json
        with open(intervals) as json_file:
            intervals = json.load(json_file)

        # validation json contents
        for interval in intervals:
            [interval[k] for k in ["region1", "region2"]]
            # add on default dup threshold if it has not been defined
            try:
                if interval["dup_threshold"] == "":
                    interval["dup_threshold"] = dup_threshold
            except KeyError:
                interval["dup_threshold"] = dup_threshold

        return intervals

    @classmethod
    def _filter_df(cls, df, filters):
        """ Filter df.
        :param: df: Pandas dataframe
        :parma: filter: Filter values as a dictionary
        :returns: filtered Pandas dataframe
        """
        query = " & ".join(
            ['{} == "{}"'.format(k, v) for k, v in filters.items()]
        )
        filtered_df = df.query(query)

        return filtered_df

    @classmethod
    def _get_sample_id(cls, file, cov_file_pattern):
        """ Method to return sample ID from file name.
        :param: file: Input file name
        :param: cov_file_pattern: Coverage file suffix to remove from filename
        :returns: sample id string
        """
        sample_id = (
            os.path.basename(file).split(cov_file_pattern)[0].replace("-", "_")
        )

        return sample_id

    def _compare_metric_at_intervals(self, cov_chunks, pair, metric):
        """ Method to compare normalised coverage at given intervals and score
        with a theshold value.
        :param: cov_chunks: List of Dataframes containing coverage info
        :param: pair: Dictionary containing info of intervals to be compared
        :param: metric: Column name in the df corresponding to the metric that
                        needs to be compared.
        :returns: Pandas dataframe
        """
        # logging
        print(
            "[{0}] Comparing {1} at {2} with {3}.".format(
                datetime.now(),
                metric,
                ",".join([str(i) for i in pair["region1"].values()]),
                ",".join([str(i) for i in pair["region2"].values()]),
            )
        )
        # iterate over each df chunk
        chunk_list = []
        for df in cov_chunks:
            for region in ["region1", "region2"]:
                # filter df for region of interest
                filt = self._filter_df(
                    df=df,
                    filters={
                        key: value
                        for key, value in pair[region].items()
                        if not key == "name"
                    },
                )
                if filt.shape[0] == 1:
                    # rename the interval for clarity
                    filt["name"] = pair[region]["name"]
                    chunk_list.append(filt)
                    # add on sample id column
                    filt["sample_id"] = self.sample_id

        # concatent the list or dataframe rows into a dataframe
        intv_comp = pd.concat(chunk_list)
        # convert from long to wide
        intv_comp = intv_comp.pivot(
            index="sample_id", columns="name", values=metric
        )
        # calc fold change between the two values
        intv_comp["fold_change"] = round(
            (
                intv_comp[pair["region1"]["name"]]
                / intv_comp[pair["region2"]["name"]]
            ),
            9,
        )
        # take a log of the fold change
        intv_comp["log2_fold_change"] = round(
            np.log2(intv_comp["fold_change"]), 9
        )

        # is the score above given theshold?
        intv_comp["above_cut_off"] = "FALSE"
        intv_comp.loc[
            intv_comp["fold_change"] > pair["dup_threshold"], "above_cut_off",
        ] = "TRUE"

        # reset index and sort
        intv_comp = intv_comp.reset_index().sort_values(
            by=["fold_change", "sample_id"], ascending=False
        )
        # order the columns
        intv_comp = intv_comp[
            [
                "sample_id",
                pair["region1"]["name"],
                pair["region2"]["name"],
                "fold_change",
                "log2_fold_change",
                "above_cut_off",
            ]
        ]

        return intv_comp

    def _process_file(self, file, intervals, out_dir):
        """ Method to process the coverage file to identify potential
        breakpoints.
        :param: file: Path to coverage file
        :param: intervals: Path of interval json file
        :param: out_dir: Path to output fir
        :returns: Writes a list of coverage comparisons and returns
                True if file processed, othwise False.
        """
        print(
            "[{0}] Processing {1}".format(
                datetime.now(), os.path.basename(file)
            )
        )
        # add to self so can be used elsewhere
        self.file = file
        # get sample
        self.sample_id = self._get_sample_id(
            file=self.file, cov_file_pattern=self.cov_file_pattern
        )
        # parse interval file to extract which region we want to process
        try:
            intervals = self._import_intervals(
                intervals=intervals, dup_threshold=self.dup_threshold
            )
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write(
                "[{0}] Error: {1} interval file wrong format! Exiting...!"
                .format(
                    datetime.now(), os.path.basename(intervals)
                )
            )
            sys.exit()
        # parse the coverage file into chunks - helps with memory requirements
        # for v. large files
        try:
            cov_chunks = self._import_coverage(
                file=file, column_dtypes=self.column_dtypes
            )
        except Exception as e:
            sys.stderr.write("[{0}] Error: {1}".format(datetime.now(), str(e)))

        # for each interval pair find and compare the interval
        try:
            out_list = []
            for pair in intervals:
                out = self._compare_metric_at_intervals(
                    cov_chunks, pair, metric=self.metric
                )

                out_list.append(out)
            # concatent into single dataframe
            out_df = pd.concat(out_list, axis=0, ignore_index=True)
            # create filename
            fname = os.path.join(
                out_dir, "{0}{1}".format(self.sample_id, self.out_fname_suffix)
            )
            self.fname = fname
            # write output to file
            out_df.to_csv(fname, index=False)
            # logging
            print("[{0}] Results written to {1}".format(datetime.now(), fname))
        except Exception as e:
            sys.stderr.write("[{0}] Error: {1}".format(datetime.now(), str(e)))
            sys.stderr.write(
                "[{0}] Error: {1} tsv malformed/missing intervals".format(
                    datetime.now(), os.path.basename(file)
                )
            )

    def __call__(self, file):
        return self._process_file(
            file=file, intervals=self.intervals, out_dir=self.out_dir
        )


if __name__ == "__main__":
    # parse the command line arguments
    args = tdh_argument_parser(sys.argv[1:])
    # process the coverage file(s)
    TDHunter(
        file=args.file,
        batch=args.batch,
        intervals=args.intervals,
        dup_threshold=args.dup_threshold,
        out_dir=args.out_dir,
        out_fname_suffix=args.out_fname_suffix,
        processes=args.processes,
        cov_file_pattern=args.cov_file_pattern,
        metric=args.metric,
    )
