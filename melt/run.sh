#!/bin/bash
#SBATCH --nodes=10
#SBATCH --exclusive
#SBATCH --time=00:30:00
#SBATCH --job-name=SS-LAMMPS
#SBATCH --output=SS-LAMMPS.out
#SBATCH --error=SS-LAMMPS.err

simnodes=8
simppn=48
dbnodes=1
dbport=6780

module unload atp
export SMARTSIM_LOG_LEVEL=debug
python run-melt.py --sim_nodes=$simnodes --sim_ppn=$simppn --db_nodes=$dbnodes --db_port=$dbport
