per_sample_outs_dir=$1
cellranger=$2
thread=1

cd $per_sample_outs_dir


#$workdir/script/cellranger_annotate.sh $workdir/toDeliver/cellrangerResult/${poolID}/outs/per_sample_outs/
ls|parallel -j $thread "mkdir ../../../{}_cell_type;$cellranger annotate --id={} --matrix={}/count/sample_filtered_feature_bc_matrix.h5 --cloupe {}/count/sample_cloupe.cloupe --cell-annotation-model=auto --output-dir ../../../{}_cell_type --localcores 8 --localmem 8 --tenx-cloud-token-path=/mnt/novaoutput/shunian/pipelines/scRNA/scRNA_cellranger_pipeline/10xcloud_token.json;mkdir -p {}/count/cell_type;mv ../../../{}_cell_type/outs/* {}/count/cell_type;rm -r ../../../{}_cell_type"


