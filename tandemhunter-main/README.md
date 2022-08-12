# Tandem Hunter
## Identification of duplicated/amplified regions based on the comparison of normalise coverage between two intervals in given coverage file.

## Requirements
-   Python 2.7+/3.4+ (tested on python 2.7 and python 3.6)
-   pandas
-   numpy

A requirements file for based on python 3.6 is available in the `requirements.txt` file.

## Usage
This script assesses duplicated/amplified regions based on the comparison of
normalise coverage between two intervals in given coverage file.

It can be used to identify KMT2A/MLL partial tandem duplications and is based on
the method described by McKerrell et al., 2016, where they compare
the coverage of exon 3 and exon 27 of MLL/KMT2A.

By default the coverage file should be in the following tab-delimiter format
(PER_TARGET_COVERAGE output file from Picard CollectHsMetrics):

```
chrom	start	end	length	name	%gc	mean_coverage	normalized_coverage	min_normalized_coverage	max_normalized_coverage	min_coverage	max_coverage	pct_0x	read_count
chr1	985390	985510	121	AGRN_1	0.68595	148.669421	0.48017	0.374655	0.616889	116	191	0	400
chr1	1718744	1718901	158	GNB1_1	0.56962	373.21519	1.205404	0.74285	1.64396	230	509	0	1087
chr1	1720466	1720733	268	GNB1_2	0.552239	377.044776	1.217773	0.652416	1.547066	202	479	0	1658
```

The NEY GLH somatic pipeline use `Picard CollectHsMetrics` to generate these per
target coverage files, like so:

```bash
# example CollectHsMetrics command as used in somatic pipeline
picard -Xmx{params.xmx} CollectHsMetrics \
        INPUT={input.bam} \
        OUTPUT={output.metrics} \
        PER_TARGET_COVERAGE={output.per_target} \
        PER_BASE_COVERAGE={output.per_base} \
        REFERENCE_SEQUENCE={input.ref} \
        BAIT_SET_NAME={wildcards.sample} \
        BI={input.interval} \
        TI={input.interval} \
        VALIDATION_STRINGENCY=LENIENT \
        MAX_RECORDS_IN_RAM=500000

```

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
PositiveSample,2.284132,1.250261,1.826924138,0.869416728,TRUE
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
