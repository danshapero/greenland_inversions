
import argparse
from os.path import expanduser

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.tri import *
from scripts.elmer import *
from scripts.meshes import *
from scripts.read_dem import read_dem
from scripts.write_qgis import *

rho_g = 917.0 / 1000.0 * 9.81


# -------------------
def has_data(q, i, j):
    return ((q[i, j] != -2.0e+9)
            and (q[i+1, j] != -2.0e+9)
            and (q[i-1, j] != -2.0e+9)
            and (q[i, j+1] != -2.0e+9)
            and (q[i, j-1] != -2.0e+9))


# -------------------------
def moving_avg_filter(q, m):
    """
    Filter the gridded data `q` with a moving average over `m` grid points
    """
    ny, nx = np.shape(q)
    qf = -2.0e+9 * np.ones((ny, nx), dtype = np.float64)

    for i in range(m, ny - m):
        for j in range(m, nx - m):
            if has_data(q, i, j):
                qfij = 0.0
                total = 0
                for di in range(-m, m+1):
                    for dj in range(-m, m+1):
                        qidijdj = q[i + di, j + dj]
                        if qidijdj != -2.0e+9:
                            qfij  += qidijdj
                            total += 1
                qf[i, j] = qfij / total

    return qf


# -------------------------
def triangular_filter(q, m):
    k = min(1, int(m/2))
    return moving_avg_filter(moving_avg_filter(q, k), k)


# ------------
def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--elmer", required = True,
                        help = "Directory of Elmer result files")
    parser.add_argument("-m", "--mesh", required = True,
                        help = "Path to triangle mesh and file stem")
    parser.add_argument("-s", "--surface", required = True,
                        help = "Path to surface DEM")
    parser.add_argument("-b", "--bed", required = True,
                        help = "Path to bed DEM")
    parser.add_argument("-o", "--output", required = True,
                        help = "Output directory and file stem")
    parser.add_argument("-p", "--partitions", required = True,
                        help = "Number of mesh partitions")

    args, _ = parser.parse_known_args(argv)

    mesh_file = args.mesh
    elmer_dir = args.elmer
    out_file = args.output
    partitions = int(args.partitions)
    surf_file = args.surface
    bed_file  = args.bed

    # Read in the surface and bed elevations
    x, y, b = read_dem(bed_file)
    _, _, s = read_dem(surf_file)

    ny, nx = np.shape(s)
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # Filter out any oscillations in the surface elevation that occur
    # over the width of ~1 ice thickness
    m = int(1000 / dx)
    s = triangular_filter(s, m)

    h = s - b

    # Compute the driving stresses
    taudx = -9999.0 * np.ones((ny, nx), dtype = np.float64)
    taudy = -9999.0 * np.ones((ny, nx), dtype = np.float64)

    for i in range(1, ny-1):
        for j in range(1, nx-1):
            if has_data(s, i, j):
                taudy[i,j] = -0.5 * rho_g * h[i,j] * (s[i+1, j] - s[i-1, j])/dy
                taudx[i,j] = -0.5 * rho_g * h[i,j] * (s[i, j+1] - s[i, j-1])/dx


    # Read in the mesh
    xm, ym, ele, bnd = read_triangle_mesh(expanduser(mesh_file))
    tri = Triangulation(xm, ym, ele)

    # Get the depth-averaged computed velocities from Elmer
    um = get_field("velocity 1", elmer_dir, partitions,
                   tri, surface = "average")
    vm = get_field("velocity 2", elmer_dir, partitions,
                   tri, surface = "average")

    # Interpolate the depth-averaged velocities to the same grid as the DEMs
    finder = tri.get_trifinder()
    interp_u = LinearTriInterpolator(tri, um, finder)
    interp_v = LinearTriInterpolator(tri, vm, finder)

    u = -9999.0 * np.ones((ny, nx), dtype = np.float64)
    v = -9999.0 * np.ones((ny, nx), dtype = np.float64)

    for i in range(1, ny-1):
        for j in range(1, nx-1):
            k = int(finder(x[j], y[i]))
            if k != -1:
                u[i, j] = interp_u(x[j], y[i])
                v[i, j] = interp_v(x[j], y[i])

    write_to_qgis(out_file + "_vx.txt", u, x[0], y[0], dx, -9999.0)
    write_to_qgis(out_file + "_vy.txt", v, x[0], y[0], dx, -9999.0)
    write_to_qgis(out_file + "_taudx.txt", taudx, x[0], y[0], dx, -9999.0)
    write_to_qgis(out_file + "_taudy.txt", taudy, x[0], y[0], dx, -9999.0)


if __name__ == "__main__":
    main(sys.argv[1:])
