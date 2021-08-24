import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from smartredis import Client


def plot_timestep(n_ranks, t_step, cluster):

    # connect SmartRedis Python client
    print("starting client connection", flush=True)
    client = Client(cluster=False)

    # Create empty lists that we will fill with simulation data
    atom_id = []
    atom_type = []
    atom_x = []
    atom_y = []
    atom_z = []

    # Loop over MPI ranks and fetch the data
    # associated with each MPI rank at a given time step.
    # Each variable is saved in a separate list.
    for i in range(n_ranks):

        dataset_key = f"atoms_rank_{i}_tstep_{t_step}"

        print(f"Retrieving DataSet {dataset_key}")

        key_exists = client.poll_key(dataset_key, 5000, 60)
        if not key_exists:
            raise Exception("Timeout waiting for new data to plot")

        dataset = client.get_dataset(dataset_key)

        atom_id.extend(dataset.get_tensor("atom_id"))
        atom_type.extend(dataset.get_tensor("atom_type"))
        atom_x.extend(dataset.get_tensor("atom_x"))
        atom_y.extend(dataset.get_tensor("atom_y"))
        atom_z.extend(dataset.get_tensor("atom_z"))

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title(f'Atom position at time step {str(t_step)}')
    ax.scatter(atom_x, atom_y, atom_z, s=2)
    fig.show()
    plt.savefig(f'atom_position_{str(t_step)}.pdf')


if __name__ == "__main__":

    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--ranks", type=int, default=1)
    argparser.add_argument("--steps", type=int, default=1000)
    argparser.add_argument("--cluster", type=bool, default=False)
    args = argparser.parse_args()

    n_ranks = args.ranks
    t_step = args.steps
    cluster= args.cluster

    for i in range(0, t_step, 50):
        plot_timestep(n_ranks, i, cluster)
