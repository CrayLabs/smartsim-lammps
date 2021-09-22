#!/bin/bash
#COBALT -t 01:00:00
#COBALT -n 128
#COBALT -q default
#COBALT -A datascience

launcher=cobalt  # launcher for the run (slurm or cobalt)
simnodes=60       # number of nodes for LAMMPS (mind resources listed above)
simppn=64        # procs per node for LAMMPS
simsteps=1000    # number of steps for LAMMPS
simscale=4       # scale factor for LAMMPS (max = 16)
dbnodes=10        # number of DB nodes (if 3 or greater, you must change cluster flag in analysis script)
dbport=6780      # port for the DB
vis_workers=64   # number of workers to pull data for the visualization (max = nproc on single node)

module unload atp
module load miniconda-3/2021-07-28
conda activate /home/spartee/dev/miniconda/envs/smartsim/
export SMARTSIM_LOG_LEVEL=debug

python run-melt.py --launcher=$launcher --sim_nodes=$simnodes --sim_ppn=$simppn --sim_steps=$simsteps --sim_scale=$simscale \
--db_nodes=$dbnodes --db_port=$dbport --vis_workers=$vis_workers --save
