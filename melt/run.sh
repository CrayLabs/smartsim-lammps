#!/bin/bash
#SBATCH --nodes=12
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --job-name=SS-LAMMPS
#SBATCH --output=SS-LAMMPS.out
#SBATCH --error=SS-LAMMPS.err

simnodes=8        # number of nodes for LAMMPS (mind resources listed above)
simppn=48         # procs per node for LAMMPS
simsteps=10000    # number of steps for LAMMPS
simscale=1        # scale factor for LAMMPS (max = 16)
dbnodes=3         # number of DB nodes (if 3 or greater, you must change cluster flag in analysis script)
dbport=6780       # port for the DB
client_threads=12 # number of threads for the client dataset aggregation (optimum is client_threads = dbnodes)

module unload atp
export SMARTSIM_LOG_LEVEL=debug

python run-melt.py --sim_nodes=$simnodes --sim_ppn=$simppn --sim_steps=$simsteps --sim_scale=$simscale \
--db_nodes=$dbnodes --db_port=$dbport --client_threads=$client_threads --save
