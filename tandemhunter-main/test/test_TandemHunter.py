# Unit tests for Tandem Hunter
# Author: Helena L. Spiewak
# Date created: 2021-04-07
# Date modified:

from ..TandemHunter import TDHunter, tdh_argument_parser
import pytest
import os
import csv
import glob


class BaseTest(object):
    intervals = "./test/test_intervals.json"
    out_dir = "./test/test_output"
    cov_file_pattern = ".qc.coverage.txt"
    out_fname_suffix = "*.cvg_comparison.csv"

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        # find breakpoints results files
        files = glob.glob(
            os.path.join(self.out_dir, self.out_fname_suffix), recursive=True,
        )
        # delete them
        [os.remove(f) for f in files]


class TestTDHunterAll(BaseTest):
    def check_file(self, output_file, output_contents):
        """ Check results files.
        :param: output_file: Output file to check
        :param: output_contents: Expected output contents
        :returns: Asserts each line is true
        """
        # check file created
        assert os.path.isfile(output_file)

        # open file and check candidate breakpoints
        with open(output_file, "r") as results:
            results_reader = csv.reader(results)
            n = 0
            for row in results_reader:
                assert row == output_contents[n]
                n += 1
            # check number of breakpoints as expected
            assert n == len(output_contents)

    def test_with_positive_file(self):
        """ No error if file argument given and results file generated that
        contains positive results """
        file = "./test/PositiveSample.qc.coverage.txt"
        # initiate class
        td = TDHunter(file=file, intervals=self.intervals, out_dir=self.out_dir)
        assert td

        # check and contents
        self.check_file(
            output_file=td.fname,
            output_contents=[
                [
                    "sample_id",
                    "MLL_EXON3",
                    "MLL_EXON27",
                    "fold_change",
                    "log2_fold_change",
                    "above_cut_off",
                ],
                [
                    "PositiveSample",
                    "2.284132",
                    "1.250261",
                    "1.826924138",
                    "0.869416728",
                    "TRUE",
                ],
            ],
        )

    def test_with_negative_file(self):
        """ No error if file argument given and results file generated that
        contains negative results """
        file = "./test/NegativeSample.qc.coverage.txt"
        # initiate class
        td = TDHunter(file=file, intervals=self.intervals, out_dir=self.out_dir)
        assert td

        # check and contents
        self.check_file(
            output_file=td.fname,
            output_contents=[
                [
                    "sample_id",
                    "MLL_EXON3",
                    "MLL_EXON27",
                    "fold_change",
                    "log2_fold_change",
                    "above_cut_off",
                ],
                [
                    "NegativeSample",
                    "1.237117",
                    "1.187973",
                    "1.041367944",
                    "0.058479903",
                    "FALSE",
                ],
            ],
        )

    def test_with_interval_json_no_dup_threshold(self):
        """ No error if interval json file does not have dup_threshold defined. """
        file = "./test/PositiveSample.qc.coverage.txt"
        intervals = "./test/test_intervals_no_dup_threshold.json"
        # initiate class
        td = TDHunter(file=file, intervals=intervals, out_dir=self.out_dir)
        assert td

        # check and contents
        self.check_file(
            output_file=td.fname,
            output_contents=[
                [
                    "sample_id",
                    "MLL_EXON3",
                    "MLL_EXON27",
                    "fold_change",
                    "log2_fold_change",
                    "above_cut_off",
                ],
                [
                    "PositiveSample",
                    "2.284132",
                    "1.250261",
                    "1.826924138",
                    "0.869416728",
                    "TRUE",
                ],
            ],
        )

    def test_initiation_with_batch(self):
        """ No error if batch argument given """
        td = TDHunter(
            batch="./test/Batch", out_dir=self.out_dir, intervals=self.intervals
        )
        assert td
        # check 2 results file created
        results_files = glob.glob(
            os.path.join(self.out_dir, self.out_fname_suffix), recursive=True
        )
        assert len(results_files) == 2

    def test_system_exit_no_file_batch(self):
        """ Initiation with no file or batch argument causing system exit """
        with pytest.raises(SystemExit):
            TDHunter()

    def check_invalid_file(self, capsys, file, expected_stderr):
        """ Method to check invalid file.
        :param: file: Path to test file
        :param: expected_stderr: Expected stderr content
        :returns: Asserts file doesn't exists and stderr message
        """
        # initiate class
        td = TDHunter(file=file, intervals=self.intervals, out_dir=self.out_dir)
        assert td
        # checkout std err message in output
        captured = capsys.readouterr()
        for err in expected_stderr:
            assert err in captured.err
        # check that no file was created
        try:
            td.fname
        except AttributeError:
            assert True

    def test_with_bad_header_file(self, capsys):
        """ Error if coverage file has bad header """
        file = "./test/BadHeader.qc.coverage.txt"
        self.check_invalid_file(
            capsys=capsys,
            file=file,
            expected_stderr=[
                "cannot safely convert passed user dtype",
                "coverage file is invalid",
            ],
        )

    def test_with_missing_intervals_file(self, capsys):
        """ Error if file does not contain the given intervals """
        file = "./test/MissingIntervals.qc.coverage.txt"
        self.check_invalid_file(
            capsys=capsys,
            file=file,
            expected_stderr=[
                "No objects to concat",
                "coverage file is invalid",
            ],
        )

    def test_with_malformed_intervals_file(self, capsys):
        """ SystemExit if interval file not as expected """
        file = "./test/MissingIntervals.qc.coverage.txt"
        intervals = "./test/test_intervals_malformed.json"
        with pytest.raises(SystemExit):
            TDHunter(file=file, intervals=intervals)

class TestFindCoverageFiles(BaseTest):
    def test_coverage_file_present(self):
        """ Returns a list of paths to coverage file if given correct
        directory containing expected coverage files """
        coverage_files = TDHunter._find_coverage_files(
            batch_dir="./test/Batch", cov_file_pattern=self.cov_file_pattern
        )
        # returns a list of length 1
        assert isinstance(coverage_files, list)
        assert len(coverage_files) == 2

    def test_coverage_file_not_present(self):
        coverage_files = TDHunter._find_coverage_files(
            batch_dir="./test/EmptyBatch",
            cov_file_pattern=self.cov_file_pattern,
        )
        # returns a list of length 0
        assert isinstance(coverage_files, list)
        assert len(coverage_files) == 0


class TestTDHArgsParser(BaseTest):
    def test_parser_file(self):
        """ File argument should be as expected """
        file = "./test/PositiveSample.qc.coverage.txt"
        parser = tdh_argument_parser(
            ["-F", file, "--intervals", self.intervals]
        )
        assert parser.file == file

    def test_parser_batch(self):
        """ Batch argument should be as expected """
        batch = "./test/"
        parser = tdh_argument_parser(
            ["-B", batch, "--intervals", self.intervals]
        )
        assert parser.batch == batch
