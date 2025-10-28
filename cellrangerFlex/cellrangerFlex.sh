
workdir="/mnt/novaoutput/shunian/scRNA/cellrangerOnly/25300-01"
projectID="25300-01"
outputdir="$workdir/toDeliver/cellrangerResult"
fastqdir="/mnt/novaoutput/Delivery_Team/1-Analysis/25300-01_S1-2025-10-16-09/SampleSheet-101325-891-XB-fcB--10nt-10nt-1-mismatch-2025-10-16-09"
cellranger="/mnt/novaoutput/shunian/pipelines/scRNA/tools/cellranger-9.0.1/cellranger"
species="mouse"
sampleInfo_file="$workdir/script/sampleInfo.csv" ## sample_id,probe_barcode_ids,description| sample1,BC001,Control| sample2,BC003,Treated
name="25300XC-01"

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

touch $workdir/script/${projectID}_config.csv
echo "[gene-expression]" >$workdir/script/${projectID}_config.csv
echo "reference,$refGenome" >>$workdir/script/${projectID}_config.csv
echo "probe-set,$probeSet" >>$workdir/script/${projectID}_config.csv
echo "create-bam,true" >>$workdir/script/${projectID}_config.csv
echo " " >>$workdir/script/${projectID}_config.csv
echo "[libraries]" >>$workdir/script/${projectID}_config.csv
echo "fastq_id,fastqs,feature_types" >>$workdir/script/${projectID}_config.csv
echo "$name,$fastqdir,Gene Expression" >>$workdir/script/${projectID}_config.csv
echo " " >>$workdir/script/${projectID}_config.csv
echo "[samples]" >>$workdir/script/${projectID}_config.csv
cat $sampleInfo_file >>$workdir/script/${projectID}_config.csv

$cellranger multi --id $name --csv $workdir/script/${projectID}_config.csv --output-dir $outputdir 

