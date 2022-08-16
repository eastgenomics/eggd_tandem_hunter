# egg_tandem_hunter v1.0.0
This app has been adapted in house to work for samples aligned to b38 reference.

## Requirements
-   Python 2.7+/3.4+ (originally tested on python 2.7 and python 3.6)
-   pandas
-   numpy

A requirements file for based on python 3.6 is available in the `requirements.txt` file.

## Identification of duplicated/amplified regions based on the comparison of normalise coverage between two intervals in given coverage file.

## Usage
TandemHunter.py assesses duplicated/amplified regions based on the comparison of
normalise coverage between two intervals in given coverage file.

It can be used to identify KMT2A/MLL partial tandem duplications and is based on
the method described by McKerrell et al., 2016, where they compare
the coverage of exon 3 and exon 27 of MLL/KMT2A.

By default the coverage file should be in the following tab-delimiter format
(PER_TARGET_COVERAGE output file from Picard CollectHsMetrics):

```
chrom	start	end	length	name	%gc	mean_coverage	normalized_coverage	min_normalized_coverage	max_normalized_coverage	min_coverage	max_coverage	pct_0x	read_count
chr11	118436493	118436944	452	.	0.792035	2120.834071	0.750534	0.4735	0.952308	1338	2691	0	10154
chr11	118468776	118468844	69	.	0.463768	5666.768116	2.005392	1.758461	2.115179	4969	5977	0	8063
chr11	118471663	118474315	2653	.	0.455711	7069.555974	2.501819	1.547899	2.771638	4374	7832	0	164434
```

The East GLH somatic pipeline use `eggd Picard QC v1.0.0` to generate these per
target coverage files. NOTE: The exact coordinates for exons 3 and 27 need to be in the
PER_TARGET_COVERAGE output file, this can be done by running Picard using
egg_tandem_hunter/Picard_inputs/KMT2A_all_exons.bed

It can be run with a single file (with `-F` or `--file` switch) or a batch of
coverage files (`-B` or `--batch` switch) as shown below. One of these has to be
given, but not both.

```
# Pass in a batch directory and write to specified directory
python TandemHunter.py -B test/Batch -O /path/to/output_dir

# Pass in a single coverage file and write to specified directory
python TandemHunter.py -F test/PositiveSample.qc.coverage.txt -O /path/to/output_dir

```

A full list of additional arguments can be viewed by `python TandemHunter.py --help`.

Coverage comparisons are written to a file called `.cvg_comparison.csv` in the present working directory by default.

An example of the contents of a `.cvg_comparison.csv` file is given below.

```
sample_id,MLL_EXON3,MLL_EXON27,fold_change,log2_fold_change,above_cut_off
2204845_22144Z0041_1_BM_MPD_MYE_M_EGG2_S39_L001_markdup.pertarget_,2.501819,0.9739260000000001,2.568797835,1.361093354,TRUE

```

generate_comparison_csv_to_xls.py
generate_comparison_csv_to_xls.py takes outputs from tandemhunter to
make a single .xlsx spreadsheet named comparison_csv.xlsx

An example of it's contents comparison_csv.xlsx is given below.

```
sample_id	MLL_EXON3	MLL_EXON27	fold_change	log2_fold_change	above_cut_off
2109981_21315Z0106_1_BM_MPD_MYE_M_EGG2_S8_L001_markdup.pertarget_	1.469901	1.470338	0.999702789	-0.000428849	False
2202920_22084Z0046_1_BM_AML_MYE_M_EGG2_S2_L001_markdup.pertarget_	1.452241	1.476602	0.983501986	-0.024000129	False
2204519_22131Z0009_1_BM_MPD_MYE_M_EGG2_S9_L001_markdup.pertarget_	1.444375	1.471847	0.981335016	-0.027182356	False
```
## Testing
The following non-base module(s) are required for running the unit tests. These
are defined in the `requirements.txt` file.
-   pytest
-   pytest-cov

To run the unit tests and assess code coverage, run the following command.

```bash
# run this line in the base directory for the module
pytest --cov=TandemHunter --cov-report term-missing -v test
```

Originally developed by NEY GLH Bioinformatics Team.
