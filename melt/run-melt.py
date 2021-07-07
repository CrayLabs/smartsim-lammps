from smartsim import Experiment, slurm
from smartsim.settings import RunSettings
from smartsim.database import Orchestrator

# Create a SmartSim Experiment using the default
experiment = Experiment("lammps_experiment")

lmps = RunSettings("lmp", "-i in.melt", run_command="mpirun", run_args={"-np": "6"})


# Create the LAMMPS SmartSim model entity with the previously
# defined run settings
lammps = experiment.create_model("lammps",
                                 run_settings=lmps)

# Attach the simulation input file in.melt to the entity so that
# the input file is copied into the experiment directory when it is created
lammps.attach_generator_files(to_copy=["./in.melt"])

db = Orchestrator()

# Generate the experiment directory structure and copy the files
# attached to SmartSim entities into that folder structure.
experiment.generate(lammps, db, overwrite=True)

# Start the model and orchestrator
experiment.start(lammps, db, summary=True)

# When the model and analysis script are complete, stop the
# orchestrator with the stop() call which will
# stop all running jobs when no entities are specified
#experiment.stop(db)

