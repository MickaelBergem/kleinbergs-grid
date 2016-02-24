#!/usr/bin/python3
"""
Kleinberg's grid

@author: Mickaël Bergem
"""
from chrono import chrono
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

# Grid size
N = 100
# Kleinberg parameter
# r = 2.

# Shortcuts grid, defaults to -1
shortcuts = np.empty((N, N))
for i in range(N):
    for j in range(N):
        shortcuts[i, j] = -1

def get_shortcut(x, y, r, global_distance_grid):
    """ Returns the shortcut for node (x, y) """
    s = shortcuts[x, y]
    if s == -1:
        return new_shortcut(x, y, r, global_distance_grid)
    # Return the existing shortcut
    return s


def new_shortcut(x, y, r, global_distance_grid):
    """
    Generates a new shortcut for the given node A.

    The probability of returning node B is proportional to d(A, B)^-r
    """
    # Generate all the distance value for the grid
    local_distance_grid = global_distance_grid[N-x-1:2*N-x-1, N-y-1:2*N-y-1].copy()

    # Normalize all these values to get the distribution
    local_distance_grid /= local_distance_grid.sum()
    distribution = np.reshape(local_distance_grid, (N*N,))

    # Pick a node according to this probability distribution
    node_index = np.random.choice(N*N, p=distribution)

    # Save this shortcut
    sx = node_index // N
    sy = node_index % N
    assert distribution[node_index] == local_distance_grid[sx, sy]
    shortcuts[x, y] = node_index

    # Return it
    return node_index


def distance(ax, ay, bx, by):
    """ Returns the 'Manhattan' distance between a and b """
    return abs(ax-bx) + abs(ay - by)


@chrono
def build_distance_grid(r):
    """
    Fill the distance grid

    We assume that the reference node is at (N, N). Thanks to symmetry we can
    build the full distance grid, centered on the reference node.
    """
    global_distance_grid = np.zeros((2*N-1, 2*N-1))
    print("r:", r)
    for i in range(N):
        for j in range(1 if i==0 else 0, N):
            d = distance(0, 0, i, j) ** (-r)
            global_distance_grid[N+i-1, N+j-1] = d
            global_distance_grid[N-i-1, N+j-1] = d
            global_distance_grid[N-i-1, N-j-1] = d
            global_distance_grid[N+i-1, N-j-1] = d
    return global_distance_grid

# Distance grid for future use
# gridfilename = 'global_distance_grid{}.npy'.format(N)
# try:
#     global_distance_grid = np.load(gridfilename)
#     if global_distance_grid[N-1,N-1] != 0:
#         print("Invalid global distance grid file, computing it again!")
#         raise IOError()
#     print("Loaded the global distance grid from file.")
# except IOError:
#     global_distance_grid = np.zeros((2*N-1, 2*N-1))
#     build_distance_grid(r)
#     print("Saving the grid in {}".format(gridfilename))
#     np.save(gridfilename, global_distance_grid)


def random_dir(buffer=1000):
    while True:
        rands = np.random.randint(2, size(buffer))
        for i in range(buffer):
            yield rands[i]

def routing(params):
    """ Applies the routing algorithm and returns the number of steps """
    start_x, start_y, dest_x, dest_y = np.random.randint(N, size=(4))
    # print("Starting node: {}:{}".format(start_x, start_y))
    # print("Destination node: {}:{}".format(dest_x, dest_y))

    steps = 0
    current_x = start_x
    current_y = start_y

    r, global_distance_grid = params

    # Compute maxsteps (if no shortcut)
    maxsteps = distance(start_x, start_y, dest_x, dest_y)

    while current_x != dest_x or current_y != dest_y:
        # New step
        steps += 1
        current_distance = distance(current_x, current_y, dest_x, dest_y)
        # print("Step #{}: {}:{}, distance={}".format(steps, current_x, current_y, current_distance))

        # Grab shortcut
        shortcut = get_shortcut(current_x, current_y, r, global_distance_grid)
        sx = shortcut // N
        sy = shortcut % N
        s_distance = distance(sx, sy, dest_x, dest_y)

        if s_distance < current_distance - 1:
            # It is better to use the shortcut than the neighbors
            current_x = sx
            current_y = sy
            continue

            # Move along y
        # It is better (or equal) to use the neighbors
        if current_x == dest_x:
            direction = 1
        elif current_y == dest_y:
            # Move along x
            direction = 0
        else:
            # uniform
            direction = random_dir()

        if direction == 1:
            current_y += 1 if dest_y > current_y else -1
        else:
            current_x += 1 if dest_x > current_x else -1

    # print("Finished in {} steps!".format(steps))
    return (steps, maxsteps)

@chrono
def init_random():
    random_dir(100000)

@chrono
def run_routing(r, Ntries):
    """ Run Ntries routing for the given value of r """
    global_distance_grid = build_distance_grid(r)
    print("Running {} routings...".format(Ntries))

    steps = pool.map(routing, [(r, global_distance_grid) for _ in range(Ntries)])
    meanstep, meanmaxstep = np.sum(steps, axis=0)/Ntries
    print("Routed using {:.2f} steps on average".format(meanstep))
    return meanstep, meanmaxstep


if __name__ == '__main__':

    Ntries = 10000
    pool = Pool(4)

    r_list = list(np.arange(.1, 3, .1))
    meansteps = []
    meanmaxsteps = []

    init_random()

    for r in r_list:
        meanstep, meanmaxstep = run_routing(r, Ntries)
        meansteps.append(meanstep)
        meanmaxsteps.append(meanmaxstep)

    np.save('graph_meansteps_r{}_N{}_Ntries{}.npy'.format(r, N, Ntries), meansteps)

    plt.plot(r_list, meansteps, label="Mean steps")
    # plt.plot(r_list, meanmaxsteps, label="Max steps (if no shortcuts)")
    plt.legend()
    plt.show()
