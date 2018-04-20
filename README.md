# MobiCNV
CNV analysis based on the depth of covergae for gene panels and exomes from Miseq Reporter, Local Run Manager data or samtools (see below)

## Installation
MobiCNV is a simple python script.

### Required modules
MobiCNV requires the [xlxswriter](http://xlsxwriter.readthedocs.io/) python module

```bash
#pip install xlsxwriter
```

### clone MobiCNV

```bash
$cd /where/you/want/to/install
git clone https://github.com/mobidic/MobiCNV
```
### Inputs

MobiCNVcomputes as primary inputs csv/tsv files that are generated by the DNA enrichments workflows of [MiSeq Reporter](https://support.illumina.com/sequencing/sequencing_software/miseq_reporter.html) or [Local Run Manager](https://support.illumina.com/sequencing/sequencing_software/local-run-manager.html). You can also generate input files with a slightly modified [samtools](http://www.htslib.org/doc/samtools.html) command (see [below](#Other-pipelines)).

#### MiSeqReporter

Your input directory will be the Data/Intensities/BaseCalls/AlignmentX of your run of interest, X being '' or 2, 3... if you relaunch the analysis. The actual targets are the Sample.coverage.csv files.

#### Local Run Manager

LRM produces inside the run root a directory called 'Alignment_X', with X being 1, 2, 3 depending on the number of times you ran the analysis. Inside Alignment_X, you will find a subfolder which atually contains the data. This subfolder is your input directory. As for MSR, the actual targets are the Sample.coverage.csv files

#### [Nenufaar](https://github.com/beboche/nenufaar)

Nenufaar produces tsv files that can be directly used by MobiCNV. Your input directory is the output directory of the nenufaar analysis.

#### Other pipelines

If you use another commercial pipeline, or, better, a custom pipeline, you just need the BAM files to produce the coverage files with this command:

```bash
$samtools bedcov -Q 30 Intervals.bed sample.bam | sort -k1,1 -k2,2n -k3,3n | awk 'BEGIN {OFS="\t"}{a=($3-$2+1);b=($7/a);print $1,$2,$3,$4,b,"+","+"}' > sample_coverage.tsv
```
Intervals.bed being your ROI file. Please note it is really better to annotate your ROIs with gene names and exons (4th column) in order to interpret your data. It is also mandatory if you want to use the [gene panel](#use-a-gene-panel) option.

Put all your coverage files in a single directory which you can provide as input for MobiCNV.

### Options

#### Use a gene panel

If your Intervals bed file or Illumina manifest was annotated at least with the gene names, you can use the gene panel option, which will generate a supplementary worksheet focusing on the genes of interest. Simply provide a txt file with the gene names (one per line).

#### File format

Either tsv or csv input files.

### Run

```bash
$python MobiCNV.py -i path/to/input/directory/ -t [tsv|csv] [-p path/to/gene/panel/file.txt -o output_file.xlsx]
```

### Output

You will soon get an Excel spreadsheet, with one summary worksheet showing remarkable events and gender predictions (if ROIs include the X chr), another woksheet for autosomes, optional supplementary worksheets for sexual chromosomes and gene panels.
The fifth column shows the mean coverage for all samples for the considered ROI, with the following 3 colors traffic lights code:

-green: mean >= 100 X

-orange: 50X <= mean < 100X

-red: mean < 50X

### Remark

MobiCNV works with hg19 or hg38 data, even with hg18 in theory.

--------------------------------------------------------------------------------

**Montpellier Bioinformatique pour le Diagnostique Clinique (MoBiDiC)**

*CHU de Montpellier*

France

[Visit our website](https://neuro-2.iurc.montp.inserm.fr/mobidic/)

--------------------------------------------------------------------------------


