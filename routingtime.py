#!/usr/bin/python3
"""
Kleinberg's grid

@author: Mickaël Bergem
"""
from chrono import chrono
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np
import time

# Grid size
N = 250

Ntries = 10000

# Number of destination nodes at distance `d`
nb_nodes = [4*d for d in range(1, N)]

r_list = list(np.arange(.1, 3, .1))


def get_shortcut(x, y, random_distance, shortcuts):
    """
    Generates a new shortcut for the given node A.

    The probability of returning node B is proportional to d(A, B)^-r
    """

    # There is already a shortcut for x,y ?
    s = shortcuts[x, y]
    if s != -1:
        return s

    # print("We have no shortcut for {},{}".format(x, y))

    while(True):
        # Pick a distance according to this probability distribution
        distance = random_distance.pop()
        # print("distance:", distance)

        # Uniformly pick a node at this distance
        nb_total_nodes = nb_nodes[distance-1]
        node_index = np.random.randint(nb_total_nodes)
        ay = distance - node_index + 2*max(0, node_index - distance*2)
        ax = node_index - 2*max(node_index - distance, 0) + 2*max(0, node_index - 3 * distance)

        sx = ax + x
        sy = ay + y

        if sx < N and sy < N and sx >= 0 and sy >= 0:
            break
        # If the point is outside the map, try again

    # Save this shortcut
    shortcuts[x, y] = sx * N + sy

    # Return it
    return shortcuts[x, y]


def distance(ax, ay, bx, by):
    """ Returns the 'Manhattan' distance between a and b """
    return abs(ax-bx) + abs(ay - by)


def routing(r, shortcuts):
    """ Applies the routing algorithm and returns the number of steps """
    start_x, start_y, dest_x, dest_y = np.random.randint(N, size=(4))
    # print("Starting node: {}:{}".format(start_x, start_y))
    # print("Destination node: {}:{}".format(dest_x, dest_y))

    steps = 0
    current_x = start_x
    current_y = start_y

    # Compute maxsteps (if no shortcut)
    maxsteps = distance(start_x, start_y, dest_x, dest_y)

    # Precompute random directions
    random_directions = list(np.random.randint(2, size=(N*2)))

    # Precompute the random distances
    distribution = np.multiply(nb_nodes, [d**(-r) for d in range(1, N)])
    # Normalize all these values to get the distribution
    distribution /= distribution.sum()
    random_distance = list(np.random.choice(range(1, N), p=distribution, size=(N*N)))

    while current_x != dest_x or current_y != dest_y:
        # New step
        steps += 1
        current_distance = distance(current_x, current_y, dest_x, dest_y)
        # print("Step #{}: {}:{}, distance={}".format(steps, current_x, current_y, current_distance))

        # Grab shortcut
        shortcut = get_shortcut(current_x, current_y, random_distance, shortcuts)
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
            direction = random_directions.pop()

        if direction == 1:
            current_y += 1 if dest_y > current_y else -1
        else:
            current_x += 1 if dest_x > current_x else -1

    # print("Finished in {} steps!".format(steps))
    # print("[r{:.2f}] {} shortcuts computed".format(r, (shortcuts!=-1).sum()))

    return (steps, maxsteps)

def run_routing(params):
    """ Run Ntries routing for the given value of r """

    r, Ntries = params

    print("[{:.2f}] Running {} routings...".format(r, Ntries))

    shortcuts = np.zeros((N, N)) - 1

    steps = []
    for _ in range(Ntries):
        steps.append(routing(r, shortcuts))

    sh_computed = (shortcuts!=-1).sum()
    print("[{:.2f}] {} shortcuts computed ({:.1f}%)".format(r, sh_computed, 100.*sh_computed/N/N))

    meanstep, meanmaxstep = np.sum(steps, axis=0)/Ntries

    print("[{:.2f}] Routed using {:.2f} steps on average".format(r, meanstep))

    return meanstep
    # return meanstep, meanmaxstep


if __name__ == '__main__':

    print("Grid size: ", N)

    meansteps = []
    meanmaxsteps = []

    # Check the code out of multiprocessing
    # routing(2.0)

    pool = Pool(4)

    meansteps = pool.map(run_routing, [(r, Ntries) for r in r_list])

    np.save('graph_meansteps_N{}_Ntries{}.npy'.format(N, Ntries), meansteps)

    plt.plot(r_list, meansteps, label="Mean steps")
    # plt.plot(r_list, meanmaxsteps, label="Max steps (if no shortcuts)")
    plt.legend()
    plt.show()
