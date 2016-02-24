#!/usr/bin/python3
"""
Kleinberg's grid

@author: Mickaël Bergem
"""
from chrono import chrono
import numpy as np

# Grid size
N = 10000
# Kleinberg parameter
r = 2

# Shortcuts grid, defaults to -1
shortcuts = np.empty((N, N))
for i in range(N):
    for j in range(N):
        shortcuts[i, j] = -1

def get_shortcut(x, y):
    """ Returns the shortcut for node (x, y) """
    s = shortcuts[x, y]
    if s == -1:
        return new_shortcut(x, y)
    # Return the existing shortcut
    return s


def new_shortcut(x, y):
    """
    Generates a new shortcut for the given node A.

    The probability of returning node B is proportional to d(A, B)^-r
    """
    # Generate all the distance value for the grid
    local_distance_grid = global_distance_grid[N-x-1:2*N-x-1, N-y-1:2*N-y-1]

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
def build_distance_grid():
    """
    Fill the distance grid

    We assume that the reference node is at (N, N). Thanks to symmetry we can
    build the full distance grid, centered on the reference node.
    """

    for i in range(N):
        for j in range(1 if i==0 else 0, N):
            d = distance(0, 0, i, j) ** (-r)
            global_distance_grid[N+i-1, N+j-1] = d
            global_distance_grid[N-i-1, N+j-1] = d
            global_distance_grid[N-i-1, N-j-1] = d
            global_distance_grid[N+i-1, N-j-1] = d


# Distance grid for future use
gridfilename = 'global_distance_grid{}.npy'.format(N)
try:
    global_distance_grid = np.load(gridfilename)
    if global_distance_grid[N-1,N-1] != 0:
        print("Invalid global distance grid file, computing it again!")
        raise IOError()
    print("Loaded the global distance grid from file.")
except IOError:
    global_distance_grid = np.zeros((2*N-1, 2*N-1))
    build_distance_grid()
    np.save(gridfilename, global_distance_grid)



if __name__ == '__main__':
    print(shortcuts.shape)
    # print(global_distance_grid)
    print(get_shortcut(1,1))
