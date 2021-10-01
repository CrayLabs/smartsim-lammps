
# LAMMPS + SmartSim

LAMMPS is a popular Molecular Dyanmics (MD) library written in C++. This
repository integrates the SmartRedis C++ client into a fork (hopefully soon
to be merged) of LAMMPS for online data analysis and visualization.

An example of the interactive LAMMPS visualization with ipyvolume:

<p align="center">
  <img src="https://user-images.githubusercontent.com/13009163/135548047-a9859fa3-fec6-4ead-97ff-eaf031baac3f.png"/>
</p>

## Example: Lennard-Jones Melt Benchmark

The ``melt/`` directory demonstrates how to use SmartSim to stream
atom data, in the form of ``DataSet`` objects, to a running Python process
for data visualization.

The SmartRedis client is embedded as a atom "dump style" within LAMMPS. The
following line can be added to a LAMMPS input file to stream atom data to the
database at a given timestep interval.

```text
dump		smart_sim all atom/smartsim 100 atoms
```

The source code for the integration is located in the LAMMPS submodule as a
part of this repository in ``lammps/src/SMARTSIM``.

## Getting Started

### MiniConda

This demonstration uses MiniConda. Although it is not strictly required, we recommend its use to simplify the tracking of different environments.

MiniConda can be installed via `wget` of an appropriate installation script, such as one from

 ```https://docs.conda.io/en/latest/miniconda.html#linux-installers```

Theta users: on Theta, MiniConda is available through the module system and can be activated via the command 

```module load miniconda-3```

We recommend creating a separate environment for SmartSim and lammps

```bash
conda create --name=smartsim-lammps python=3.8.5
conda activate smartsim-lammps 
```

### Repositories

To get started, clone the `smartsim-lamps` repository

```bash
git clone --recursive https://github.com/CrayLabs/smartsim-lammps
```

You will also need the SmartRedis repository. The lammps build step later assumes that SmartRedis is in a directory parallel to ``smartsim-lammps`` named ``SmartRedis``.

```bash
git clone https://github.com/CrayLabs/SmartRedis
cd SmartRedis
make lib
```

## Additional Components

### For Theta users

Before installing additional components, Theta users must run the following commands to configure the runtime environment.

```bash
module purge
module load PrgEnv-cray
module load cray-mpich
module unload atp perftools-base cray-libsci
export CRAYPE_LINK_TYPE=dynamic
```

### git-lfs

SmartSim requires `git-lfs`. Install and configure it via the following commands

```bash
conda install git-lfs
git-lfs install
```

### Python Components

The following requirements will need to be installed in a Python environment on your system.

```text
smartsim==0.3.2
smartredis==0.2.0
ipyvolume==0.5.2
```

Install all of these requirements by running

```bash
cd smartsim-lammps/melt
pip install -r requirements.txt
smart --device cpu
```

## Setup


Next, build LAMMPS. Theta (XC users in general) users be sure to have the above
modules loaded and environment setup.

```bash
cd smartsim-lammps/lammps/cmake
mkdir build 
cd build
CC=cc CXX=CC cmake .. -DBUILD_MPI=yes -DPKG_SMARTSIM=yes
make -j 4 # or higher if you have more procs
export PATH=$(pwd):$PATH
```

## Configuring and Running the Example

The example has two batch scripts that can submit to either Cobalt (Theta)
or Slurm systems in general. These can be easily adapted to other WLMs.

In each batch script are a number of parameters that configure how LAMMPS
and the analysis will be executed.

```bash
launcher=cobalt  # launcher for the run (slurm or cobalt)
simnodes=124     # number of nodes for LAMMPS (mind resources listed above)
simppn=64        # procs per node for LAMMPS
simsteps=10000   # number of steps for LAMMPS
simscale=4       # scale factor for LAMMPS (max = 16)
dbnodes=3        # number of DB nodes (if 3 or greater, you must change cluster flag in analysis script)
dbport=6780      # port for the DB
vis_workers=64   # number of workers to pull data for the visualization (max = nproc on single node)
```

SmartSim will take care of writing the LAMMPS parameters into the configuration
file at runtime as well as launching both lammps, the database, and the analysis
out onto the system with the specified resource requirements.

The user should make sure to use their own Python environment in the batch scipt.

If a single database node is used, LAMMPS will need to be recompiled with the client
cluster flag set to false in the initializer. By default, the case is setup to run
with a 3 node database cluster.

To run the example on Theta use the following command (be sure to edit the script to point to your conda environment)

```bash
qsub run-theta.sh
```

## Data Analysis

The point of this example is to show how SmartSim can be used to perform in-transit
data analysis, however, the example can be modified to include any Python code in
the analysis script.

Currently, the analysis script generates snapshots of the atom domain at every 100 iterations.
An animation is also generated that shows the snapshots evolving through the integration
of the simulation.



