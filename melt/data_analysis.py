import time
import psutil
import matplotlib
matplotlib.use('Agg')
from multiprocessing import Pool
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from smartredis import Client


class Worker:
    def __init__(self):
        self.client = Client(cluster=False)

    def __call__(self, key):
        # returns a tuple of np.arrays
        key_exists = self.client.poll_key(key, 100, 100)
        if not key_exists:
            raise Exception("Timeout waiting for new data to plot")
        dataset = self.client.get_dataset(key)
        atom_data = (dataset.get_tensor("atom_x"),
                     dataset.get_tensor("atom_y"),
                     dataset.get_tensor("atom_z"))
        return atom_data

def worker_init():
    #print(f"Starting worker process on cpu {psutil.Process().cpu_num()}")
    global worker
    worker = Worker()

def run_worker(key):
    return worker(key)

class WorkerPool:
    def __init__(self, num_workers):
        self.pool = Pool(processes=num_workers, initializer=worker_init)

    def get_data(self, keys):
        return self.pool.map(run_worker, keys)

    def shutdown(self):
        self.pool.close()
        self.pool.join()


def plot_timestep(worker_pool, n_ranks, t_step):

    # Create empty lists that we will fill with simulation data
    atom_x = []
    atom_y = []
    atom_z = []

    dataset_keys = []
    for i in range(n_ranks):
        dataset_keys.append(f"atoms_rank_{i}_tstep_{t_step}")

    data_start = time.time()
    ts_data = worker_pool.get_data(dataset_keys)
    for data in ts_data:
        atom_x.extend(data[0])
        atom_y.extend(data[1])
        atom_z.extend(data[2])
    timings["data"] += time.time() - data_start

    plot_start = time.time()

    # Create base figure
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f'Atom position at timestep {str(t_step)}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.scatter(atom_x, atom_y, atom_z, c='g', s=2)

    timings["plot"] += time.time() - plot_start

if __name__ == "__main__":
    import sys
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--ranks", type=int, default=384)
    argparser.add_argument("--steps", type=int, default=10000)
    argparser.add_argument("--workers", type=int, default=48)
    argparser.add_argument("--save", action="store_true")
    args = argparser.parse_args()

    timings = {
        "data": 0.0,
        "plot": 0.0
    }

    # start pool of workers
    work_pool = WorkerPool(num_workers=args.workers)

    for i in range(0, args.steps, 1000):
        plot_timestep(work_pool, args.ranks, i)

    print(f"Data retrieval time: {timings['data']}")
    print(f"Plotting time: {timings['plot']}")

    work_pool.shutdown()

    if args.save:
        figs = list(map(plt.figure, plt.get_fignums()))
        for i, fig in enumerate(figs):
            canvas = FigureCanvasAgg(fig)
            canvas.print_figure(f'atom_position_{str(i * 1000)}.png', dpi=100)
