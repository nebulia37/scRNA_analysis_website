#!/bin/bash

parameter_file=$1
readarray -t params < <(awk -F',' '{print $2}' "$parameter_file")

workdir="${params[0]}"
poolID="${params[1]}"
fastqdir="${params[2]}"
species="${params[3]}"
sampleInfoFile="${params[4]}"
fastq_id="${params[5]}"
cellranger="${params[6]}"

outputdir=$workdir/toDeliver/cellrangerResult/$poolID
mkdir -p $outputdir
sampleInfo_file=$workdir/script/$sampleInfoFile

if [ $species = "mouse" ]
then
    refGenome="/mnt/novaoutput/shunian/pipelines/scRNA/GenomeDB/refdata-gex-GRCm39-2024-A"
    probeSet="/mnt/novaoutput/shunian/pipelines/scRNA/tools/cellranger-9.0.1/probe_sets/Chromium_Mouse_Transcriptome_Probe_Set_v1.1.1_GRCm39-2024-A.csv" #cellranger-x.y.z/probe_sets/Chromium_Human_Transcriptome_Probe_Set_v1.0.1_GRCh38-2020-A.csv
fi

if [ $species = "human" ]
then
    refGenome="/mnt/novaoutput/shunian/pipelines/scRNA/GenomeDB/refdata-gex-GRCh38-2020-A"
    probeSet="/mnt/novaoutput/shunian/pipelines/scRNA/tools/cellranger-9.0.1/probe_sets/Chromium_Human_Transcriptome_Probe_Set_v1.1.0_GRCh38-2024-A.csv"
fi

touch $workdir/script/${poolID}_config.csv
echo "[gene-expression]" >$workdir/script/${poolID}_config.csv
echo "reference,$refGenome" >>$workdir/script/${poolID}_config.csv
echo "probe-set,$probeSet" >>$workdir/script/${poolID}_config.csv
echo "create-bam,true" >>$workdir/script/${poolID}_config.csv
echo " " >>$workdir/script/${poolID}_config.csv
echo "[libraries]" >>$workdir/script/${poolID}_config.csv
echo "fastq_id,fastqs,feature_types" >>$workdir/script/${poolID}_config.csv
echo "$fastq_id,$fastqdir,Gene Expression" >>$workdir/script/${poolID}_config.csv
echo " " >>$workdir/script/${poolID}_config.csv
echo "[samples]" >>$workdir/script/${poolID}_config.csv
cat $sampleInfo_file >>$workdir/script/${poolID}_config.csv

$cellranger multi --id $fastq_id --csv $workdir/script/${poolID}_config.csv --output-dir $outputdir 

