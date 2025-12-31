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
parallel -j $threads --joblog run_cellranger_script.log --results $workdir/logs < $workdir/script/run_cellranger_script.sh 

if [ $? -ne 0 ];then
    echo $?
    echo "Error Occured in cellranger step"
    exit
fi

for fastq_id in $sname
do
    # remove content not useful
    if [ -d $workdir/toDeliver/cellrangerResult/${fastq_id}/outs ]; then
        mkdir -p $workdir/toDeliver/cellrangerResult/${fastq_id}_tmp
        mv $workdir/toDeliver/cellrangerResult/${fastq_id}/outs/* $workdir/toDeliver/cellrangerResult/${fastq_id}_tmp/
        rm -r $workdir/toDeliver/cellrangerResult/${fastq_id}
        mv $workdir/toDeliver/cellrangerResult/${fastq_id}_tmp $workdir/toDeliver/cellrangerResult/${fastq_id}
    fi    
    # run cellranger annotate and put it in the result folder
    cd $workdir/toDeliver/cellrangerResult/${fastq_id}
    $workdir/script/cellranger_annotate_count.sh $workdir/toDeliver/cellrangerResult/${fastq_id} ${fastq_id} $cellranger
done
