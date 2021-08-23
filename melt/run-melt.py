from smartsim import Experiment, slurm
from smartsim.settings import RunSettings, SrunSettings
from smartsim.database import Orchestrator, SlurmOrchestrator
from smartredis import Client

# Create a SmartSim Experiment using the default
experiment = Experiment("lammps_experiment", launcher="slurm")

exe = "/lus/cls01029/spartee/poseidon/smartsim-lammps/lammps/cmake/build/lmp"

lmps = SrunSettings(exe, exe_args="-i in.melt")
lammps = experiment.create_model("lammps",
                                 run_settings=lmps)
lammps.attach_generator_files(to_copy=["./in.melt"])

# create atom visualizer model reference
vis_settings = SrunSettings("python", "data_analysis.py")
vis_settings.set_nodes(1)
vis_settings.set_tasks(1)

vis_model = experiment.create_model("atom_viz", vis_settings)
vis_model.attach_generator_files(to_copy=["./data_analysis.py"])

# Create database
db = SlurmOrchestrator(port=6780,
                       db_nodes=1,
                       batch=False,
                       interface="ipogif0")

experiment.generate(lammps, db, vis_model, overwrite=True)

# Start the model and orchestrator
experiment.start(lammps,
                 vis_model,
                 db,
                 block=True,
                 summary=True)

experiment.stop(db)


#if __name__ == "__main__":
#    import argparse
#    parser = argparse.ArgumentParser(description="Run Lennard-Jones Melt Experiment")
#    parser.add_argument("--sim_nodes", type=int, default=1, help="Number of nodes for LAMMPS to run on")
#    parser.add_argument("--db_nodes", type=int, default=1, help="Number of nodes for the database to run on")

