#!/bin/bash
#SBATCH --job-name="customized_genome"
#SBATCH --export=ALL
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G


#run build

/mnt/novaoutput/shunian/tools/cellranger-arc-2.0.2/cellranger-arc mkref --config=./monkey_arc_make_customized_genome.config
