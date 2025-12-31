#!/bin/bash

parameter_file=$1
readarray -t params < <(awk -F',' '{print $2}' "$parameter_file")

workdir="${params[0]}"
fastqdir="${params[1]}"
species="${params[2]}"
cellranger="${params[3]}"
threads="${params[4]}"

echo "workdir: $workdir"
echo "fastqdir: $fastqdir"
echo "species: $species"
echo "cellranger: $cellranger"
echo "threads: $threads"

if [ $species = "mouse" ]
then
    refGenome="/mnt/novaoutput/shunian/pipelines/scRNA/GenomeDB/refdata-gex-GRCm39-2024-A"
fi

if [ $species = "human" ]
then
    refGenome="/mnt/novaoutput/shunian/pipelines/scRNA/GenomeDB/refdata-gex-GRCh38-2024-A"
fi

touch run_cellranger_script.sh
: >run_cellranger_script.sh

cd $fastqdir
sname=`ls *gz | cut -d_ -f1|sort -u`
for fastq_id in $sname
do
    outputdir=$workdir/toDeliver/cellrangerResult/${fastq_id}
    mkdir -p $outputdir
    echo "$cellranger count --id ${fastq_id} --create-bam true --transcriptome $refGenome --fastqs $fastqdir --sample ${fastq_id} --output-dir $outputdir --localcores 8 --localmem 8" >>$workdir/script/run_cellranger_script.sh
done
cd $workdir/script
chmod +x run_cellranger_script.sh

mkdir -p $workdir/logs
nohup parallel -j $threads --joblog run_cellranger_script.log --results $workdir/logs < $workdir/script/run_cellranger_script.sh &
