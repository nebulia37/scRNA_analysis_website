
workdir="/mnt/novaoutput/shunian/scRNA/cellrangerOnly/25213-04-gex"
projectID="25213-04-07"
outputdir="$workdir/toDeliver/25213-04-07"
cellranger="/mnt/novaoutput/shunian/pipelines/scRNA/tools/cellranger-9.0.1/cellranger"
name="25213-04-07"

$cellranger multi --id $name --csv $workdir/script/${projectID}_config.csv --output-dir $outputdir 

