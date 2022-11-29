import time
import psutil
import os
import numpy as np
from smartredis import Client
import ipyvolume as ipv

def plot_timestep(client, n_ranks, t_step):

    # Create empty lists that we will fill with simulation data
    atom_x = []
    atom_y = []
    atom_z = []

    # Poll for all ranks to have sent their timestep data
    list_name = f"tstep_{t_step}"
    client.poll_list_length(list_name, n_ranks, 50, 10000)

    # Multithreaded retrieval of timestep datasets
    data_start = time.time()
    datasets = client.get_datasets_from_list(f"tstep_{t_step}")
    timings["data"] += time.time() - data_start
    dt = time.time() - data_start
    print(f"Data retrieval took {dt}")
    for dataset in datasets:
        atom_x.extend(dataset.get_tensor("atom_x"))
        atom_y.extend(dataset.get_tensor("atom_y"))
        atom_z.extend(dataset.get_tensor("atom_z"))


    # convert to numpy
    x = np.array(atom_x)
    y = np.array(atom_y)
    z = np.array(atom_z)

    plot_start = time.time()

    # Use Ipyvolume to plot the data
    if args.save:
        ipv.scatter(x, y, z, size=.5, marker='sphere', color='green')
        ipv.save(f'atom_position_{str(t_step)}.html')
        ipv.clear()

    timings["plot"] += time.time() - plot_start

    dt = time.time() - plot_start
    print(f"Data plot took {dt}")

    # add to final list for animation
    ATOMS_X.append(x)
    ATOMS_Y.append(y)
    ATOMS_Z.append(z)

if __name__ == "__main__":

    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--ranks", type=int, default=384)
    argparser.add_argument("--steps", type=int, default=10000)
    argparser.add_argument("--save", action="store_true")
    args = argparser.parse_args()

    timings = {
        "data": 0.0,
        "plot": 0.0,
        "animation": 0.0
    }

    print(f"Using {os.environ['SR_THREAD_COUNT']} client threads.")
    # Position arrays for animation creation
    ATOMS_X = []
    ATOMS_Y = []
    ATOMS_Z = []

    # Initialize client outside of timestep loop for efficiency
    client = Client(cluster=True)

    # Gather and plot data for each time step
    for i in range(0, args.steps, 100):
        plot_timestep(client, args.ranks, i)

    # Create the animation
    if args.save:
        anim_start = time.time()
        ani = ipv.scatter(np.array(ATOMS_X),
                          np.array(ATOMS_Y),
                          np.array(ATOMS_Z), size=.5, marker='sphere', color='green')
        ipv.animation_control(ani, interval=500)
        ipv.save("Lennard-Jones-Animation.html")
        timings["animation"] = time.time() - anim_start

    print(f"Data retrieval time: {timings['data']}")

    if args.save:
        print(f"Plotting time: {timings['plot']}")
        print(f"Animation creation time: {timings['animation']}")
