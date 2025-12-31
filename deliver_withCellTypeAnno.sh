

cd $workdir/toDeliver/cellrangerResult/
folder=`ls *cell_type`
mkdir /mnt/FTP_Drive/Delivery_Team/3-Upload-BI/25296-01Q1-cellTypeAnnotation-12162025SX
cd /mnt/FTP_Drive/Delivery_Team/3-Upload-BI/25296-01Q1-cellTypeAnnotation-12162025SX
mkdir $folder 
nohup ls|parallel "cp -r $workdir/toDeliver/cellrangerResult/{}/outs/* {}/" &
