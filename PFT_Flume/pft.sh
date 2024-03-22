#!/bin/bash
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -c 1 # specify 6 threads per process
#SBATCH -t 50:00:00
#SBATCH -p workq
#SBATCH -A loni_proteus01s
#SBATCH -o o.out # optional, name of the stdout, using the job number (%j) and the first node (%N)
#SBATCH -e e.err # optional, name of the stderr, using job and first node values
#SBATCH --mail-type END
#SBATCH --mail-user rschur3@lsu.edu

date
module purge
module load proteus/1.8.1

mkdir -p $WORK/pft$SLURM_JOBID
cd $WORK/pft$SLURM_JOBID
echo $SLURM_SUBMIT_DIR
cp $SLURM_SUBMIT_DIR/*.py .
cp $SLURM_SUBMIT_DIR/pft.sh . 
cp $SLURM_SUBMIT_DIR/*.csv . 
cp $SLURM_SUBMIT_DIR/*.obj .

srun parun -F -l5 --TwoPhaseFlow pft_flume.py
exit 0

