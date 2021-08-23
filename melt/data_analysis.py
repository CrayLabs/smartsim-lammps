import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from smartredis import Client


def plot_timestep(n_ranks, t_step):

    # connect SmartRedis Python client
    client = Client(cluster=False)

    # Create empty lists that we will fill with simulation data
    atom_id = []
    atom_type = []
    atom_x = []
    atom_y = []
    atom_z = []

    # We will loop over MPI ranks and fetch the data
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

    # We plot the atom positions to check that the atom position distribution
    # is uniform, as expected.
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Atom position')
    ax.scatter(atom_x, atom_y, atom_z)
    fig.show()
    plt.savefig(f'atom_position_{str(t_step)}.pdf')


if __name__ == "__main__":

    # The command line argument "ranks" is used to
    # know how many MPI ranks were used to run the
    # LAMMPS simulation because each MPI rank will send
    # a unique key to the database.  This command line
    # argument is provided programmatically as a
    # run setting in the SmartSim experiment script.
    # Similarly, the command line argument "time"
    # is used to set which time step data will be
    # pulled from the database.  This is also set
    # programmatically as a run setting in the SmartSim
    # experiment script
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--ranks", type=int, default=1)
    argparser.add_argument("--steps", type=int, default=1000)
    args = argparser.parse_args()

    n_ranks = args.ranks
    t_step = args.steps

    for i in range(0, t_step, 100):
        plot_timestep(n_ranks, i)
