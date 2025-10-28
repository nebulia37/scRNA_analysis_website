workdir="./"
cd $workdir
cellrangerArc=/mnt/novaoutput/shunian/pipelines/scRNA/tools/cellranger-arc-2.0.2/cellranger-arc
transRef='../Macaca_mulatta_Mmul_10_114_SIVmac251_withMotif'

name="24155-06-01"
library="./24155-06-01_lib.csv"

${cellrangerArc} count --id=${name} --min-atac-count 400 --min-gex-count 400 --reference=$transRef --libraries=$library --maxjobs 2 --mempercore 2
