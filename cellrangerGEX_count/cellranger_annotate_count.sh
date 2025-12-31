count_outs_dir=$1
sampleID=$2
cellranger=$3

cd $count_outs_dir

#filtered_feature_bc_matrix.h5
#/mnt/novaoutput/shunian/scRNA/cellrangerOnly/25301-01-12-01V3-gex/toDeliver/cellrangerResult/25301-01-20V3/outs
mkdir -p ../${sampleID}_cell_type
$cellranger annotate --id=${sampleID} --matrix=filtered_feature_bc_matrix.h5 --cloupe=cloupe.cloupe --cell-annotation-model=auto --output-dir ../${sampleID}_cell_type --localcores 8 --localmem 8 --tenx-cloud-token-path=/mnt/novaoutput/shunian/pipelines/scRNA/scRNA_cellranger_pipeline/10xcloud_token.json
mkdir cell_type
mv ../${sampleID}_cell_type/outs/* cell_type/
rm -r ../${sampleID}_cell_type

