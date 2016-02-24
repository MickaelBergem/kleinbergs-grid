# What I tried

## How to find the shortcut of a given node

In the beginning, I wanted to first pick up a value for the distance and then to
uniformly pick a node among the equidistant nodes. Unfortunately, this does not
reduce the problem because the distribution is not easier to compute as the grid
is finite and there is no symmetry.

I then implemented a shortcut generator using a precomputed grid of distances:

    for i in range(N):
        for j in range(1 if i==0 else 0, N):
            d = distance(0, 0, i, j) ** (-r)
            global_distance_grid[N+i-1, N+j-1] = d
            global_distance_grid[N-i-1, N+j-1] = d
            global_distance_grid[N-i-1, N-j-1] = d
            global_distance_grid[N+i-1, N-j-1] = d

I extract then the local grid of distances from this global map, normalize it,
and randomly pick an element using this distribution.

Building the initial distance grid takes 3'40" on a single core, for N = 10000
(time complexity = O(N²)), and the grid is cached on disk.

This state is referenced by the git tag `basic-shortcut-finder`.
