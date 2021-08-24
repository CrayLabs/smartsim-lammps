from smartsim import Experiment
from smartsim.settings import SrunSettings
from smartsim.database import SlurmOrchestrator

experiment = Experiment("lammps_experiment", launcher="slurm")
exe = "/lus/cls01029/spartee/poseidon/smartsim-lammps/lammps/cmake/build/lmp"


def create_lammps_model(sim_nodes, sim_ppn):

    # Create a SmartSim Experiment using the default

    lmps = SrunSettings(exe, exe_args="-i in.melt")
    lmps.set_nodes(sim_nodes)
    lmps.set_tasks_per_node(sim_ppn)
    lammps = experiment.create_model("lammps",
                                    run_settings=lmps)
    lammps.attach_generator_files(to_copy=["./in.melt"])
    return lammps

def create_visualizer(sim_nodes, sim_ppn, db_cluster=False):
    # create atom visualizer model reference
    total_sim_ranks = int(sim_nodes) * int(sim_ppn)

    vis_settings = SrunSettings("python",
                                f"data_analysis.py --ranks={total_sim_ranks} --cluster={db_cluster}")
    vis_settings.set_nodes(1)
    vis_settings.set_tasks_per_node(1)

    vis_model = experiment.create_model("atom_viz", vis_settings)
    vis_model.attach_generator_files(to_copy=["./data_analysis.py"])
    return vis_model

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Lennard-Jones Melt Experiment")
    parser.add_argument("--sim_nodes", type=int, default=1, help="Number of nodes for LAMMPS")
    parser.add_argument("--sim_ppn", type=int, default=48, help="Number of processors per node for LAMMPS")
    parser.add_argument("--db_nodes", type=int, default=1, help="Number of nodes for the database")
    parser.add_argument("--db_port", type=int, default=6780, help="Port for the database")
    parser.add_argument("--db_interface", type=str, default="ipogif0", help="Network interface for the database")
    args = parser.parse_args()

    db_cluster = True if args.db_nodes > 1 else False
    lammps = create_lammps_model(args.sim_nodes, args.sim_ppn)
    vis = create_visualizer(args.sim_nodes, args.sim_ppn, db_cluster)

    db = SlurmOrchestrator(port=args.db_port,
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
