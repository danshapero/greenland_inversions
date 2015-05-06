
import numpy as np
import matplotlib.pyplot as plt

import sys
import argparse
from os.path import expanduser

from matplotlib.tri import *
from scripts.elmer import *
from scripts.meshes import *
from scripts.read_dem import read_dem

rho_g = 917.0 / 1000.0 * 9.81  #[kPa / m]

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

    # Read in the mesh
    x, y, ele, bnd = read_triangle_mesh(expanduser(mesh_file))
    tri = Triangulation(x, y, ele)
    nn = len(x)

    # Get the depth-averaged computed velocities from Elmer
    ux = get_field("velocity 1", elmer_dir, partitions,
                   tri, surface = "average")
    uy = get_field("velocity 2", elmer_dir, partitions,
                   tri, surface = "average")

    # Read in the surface/bed elevations
    xb, yb, bd = read_dem(bed_file)
    xs, ys, sd = read_dem(surf_file)

    b = CubicTriInterpolator(tri, gridded_to_point_cloud(x, y, xb, yb, bd))
    s = CubicTriInterpolator(tri, gridded_to_point_cloud(x, y, xb, yb, sd))

    dsdx, dsdy = s.gradient(x, y)
    taux = np.zeros(nn, dtype = np.float64)
    tauy = np.zeros(nn, dtype = np.float64)
    tauu = np.zeros(nn, dtype = np.float64)

    for k in range(nn):
        h = s(x[k], y[k]) - b(x[k], y[k])
        taux[k] = -rho_g * h * dsdx[k]
        tauy[k] = -rho_g * h * dsdy[k]

        tauu[k] = (taux[k]*ux[k] + tauy[k]*uy[k]) / np.sqrt(ux[k]**2 + uy[k]**2)

    plt.figure()
    plt.gca().set_aspect('equal')
    plt.tricontourf(x/1000.0, y/1000.0, ele, tauu, 36, shading='faceted')
    plt.colorbar(label = 'kPa')
    plt.xlabel('x (km)')
    plt.ylabel('y (km)')
    plt.title('Stress component in the flow direction')
    plt.show()

if __name__ == "__main__":
    main(sys.argv[1:])
