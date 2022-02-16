from smartsim import Experiment
from smartsim.database import Orchestrator


def create_lammps_model(experiment, sim_nodes, sim_ppn, steps, scale):

    lmps = experiment.create_run_settings(exe, run_command="auto",
                                          exe_args="-i in.melt")

    # Slurm requires the number of nodes but aprun does not support this
    if(experiment._launcher == "slurm")
        lmps.set_nodes(sim_nodes)

    lmps.set_tasks(sim_nodes*sim_ppn)
    lmps.set_tasks_per_node(sim_ppn)

    # parameters to be written into in.melt at runtime
    sim_params = {
        "TIMESTEPS": steps,
        "SCALE_X": scale,
        "SCALE_Y": scale,
        "SCALE_Z": scale
    }

    lammps = experiment.create_model("lammps",
                                     run_settings=lmps,
                                     params=sim_params)
    lammps.attach_generator_files(to_configure=["./in.melt"])
    return lammps

def create_visualizer(experiment, sim_nodes, sim_ppn, sim_steps, workers, save):
    # create atom visualizer model reference

    total_sim_ranks = int(sim_nodes) * int(sim_ppn)
    exe_args = ["data_analysis.py",
                f"--ranks={total_sim_ranks}",
                f"--workers={workers}",
                f"--steps={sim_steps}"]

    vis_settings = experiment.create_run_settings("python",
                                                  run_command="auto",
                                                  exe_args=exe_args)

    if(experiment._launcher == "slurm")
        vis_settings.set_nodes(1)

    vis_settings.set_tasks(1)
    vis_settings.set_cpus_per_task(workers)

    vis_model = experiment.create_model("atom_viz", vis_settings)
    vis_model.attach_generator_files(to_copy=["./data_analysis.py"])
    return vis_model

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Lennard-Jones Melt Experiment")
    parser.add_argument("--sim_nodes", type=int, default=1, help="Number of nodes for LAMMPS")
    parser.add_argument("--sim_ppn", type=int, default=48, help="Number of processors per node for LAMMPS")
    parser.add_argument("--sim_steps", type=int, default=10000, help="Number of timesteps for LAMMPS")
    parser.add_argument("--sim_scale", type=int, default=1, help="Scale int for LAMMPS simulation")
    parser.add_argument("--db_nodes", type=int, default=1, help="Number of nodes for the database")
    parser.add_argument("--db_port", type=int, default=6780, help="Port for the database")
    parser.add_argument("--db_interface", type=str, default="ipogif0", help="Network interface for the database")
    parser.add_argument("--vis_workers", type=int, default=48, help="Number of workers to pull data for visualizations")
    parser.add_argument("--save", action="store_true", help="Save plotted figures to file")
    args = parser.parse_args()

    # create the experiment
    experiment = Experiment("lammps_experiment", launcher="auto")
    exe = "../lammps/cmake/build/lmp"

    lammps = create_lammps_model(experiment,
                                 args.sim_nodes,
                                 args.sim_ppn,
                                 args.sim_steps,
                                 args.sim_scale)

    db_cluster = True if args.db_nodes > 1 else False
    vis = create_visualizer(experiment,
                            args.sim_nodes,
                            args.sim_ppn,
                            args.sim_steps,
                            args.vis_workers,
                            args.save)

    db = Orchestrator(launcher="auto",
                      port=args.db_port,
                      db_nodes=args.db_nodes,
                      batch=False,
                      interface=args.db_interface)

    experiment.generate(lammps,
                        vis,
                        db,
                        overwrite=True)

    # Start the model and orchestrator
    experiment.start(lammps, vis, db,
                    block=True,
                    summary=True)

    experiment.stop(db)
    print(experiment.summary())
