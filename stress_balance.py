#!/usr/bin/env python

import sys
import os
import glob
import numpy as np
import argparse
from os.path import expanduser
from matplotlib.tri import *

from scripts.meshes import read_triangle_mesh
from scripts.elmer import get_field
from scripts.read_dem import read_dem


rho     = 917.0
gravity = 9.81


# ------------
def area(x, y):
    return 0.5 * np.abs((x[1] - x[0]) * (y[2] - y[0]) -
                        (x[2] - x[0]) * (y[1] - y[0]))


# ---------------
def grad(x, y, q):
    S = np.array([[x[1] - x[0], x[2] - x[0]],
                  [y[1] - y[0], y[2] - y[0]]])
    T = np.linalg.inv(S)
    return np.dot(np.array([q[1] - q[0], q[2] - q[0]]), T)


# --------------------------------------------
def interpolate_grid_to_triangle(x, y, q, tri):
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    nn = len(tri.x)

    qtri = np.zeros(nn, dtype = np.float64)

    for n in range(nn):
        i = int( (tri.y[n] - y[0]) / dy )
        j = int( (tri.x[n] - x[0]) / dx )

        alpha_y = (tri.y[n] - y[i]) / dy
        alpha_x = (tri.x[n] - x[j]) / dx

        qtri[n] = (q[i, j]
                   + alpha_x * (q[i, j+1] - q[i, j])
                   + alpha_y * (q[i+1, j] - q[i, j])
                   + alpha_x * alpha_y * (q[i, j] + q[i+1, j+1]
                                          - q[i, j+1] - q[i+1, j]))

    return qtri


# ---------------------------------------------
def basal_stress_power(tri, u, v, tau_x, tau_y):
    """
    Given a triangulation together with velocity and basal stress fields,
    compute the total stress power, i.e., integral(stress * velocity)dA.

    Parameters:
    ==========
    tri:          a triangulation of the glacier domain in 2D
    u, v:         numpy array of glacier velocities at triangulation points
    tau_x, tau_y: basal shear stress components

    Returns:
    =======
    power: the total power dissipated by the stress and velocity fields
    """

    power = 0.0

    triangles        = tri.triangles
    num_triangles, _ = np.shape(triangles)
    x                = tri.x
    y                = tri.y

    for n in range(num_triangles):
        elem = triangles[n,:]
        a = area(x[elem], y[elem])
        B = np.array([[a/6.0,  a/12.0, a/12.0],
                      [a/12.0, a/6.0,  a/12.0],
                      [a/12.0, a/12.0, a/6.0]])
        power += (np.dot(u[elem], np.dot(B, tau_x[elem]))
                  + np.dot(v[elem], np.dot(B, tau_y[elem])))

    return power


# ---------------------------------------
def driving_stress_power(tri, u, v, s, b):
    """
    Same as last one but for driving stress.
    """
    power = 0.0

    triangles        = tri.triangles
    num_triangles, _ = np.shape(triangles)
    x                = tri.x
    y                = tri.y

    h = s - b

    for n in range(num_triangles):

        elem = triangles[n,:]
        a = area(x[elem], y[elem])
        B = np.array([[a/6.0,  a/12.0, a/12.0],
                      [a/12.0, a/6.0,  a/12.0],
                      [a/12.0, a/12.0, a/6.0]])

        ds = grad(x[elem], y[elem], s[elem])
        ht = np.dot(B, h[elem])

        power -= rho * gravity * (ds[0] * np.dot(u[elem], ht)
                                  + ds[1] * np.dot(v[elem], ht))

    return power


# ------------
def main(argv):
    mesh_file = ""
    elmer_dir = ""
    out_file  = ""
    bed_file  = ""
    surf_file = ""

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--elmer", required = True,
                        help = "Directory of Elmer result files")
    parser.add_argument("-m", "--mesh", required = True,
                        help = "Path to triangle mesh and file stem")
    parser.add_argument("-b", "--bed", required = True,
                        help = "Bed DEM file")
    parser.add_argument("-s", "--surface", required = True,
                        help = "Surface DEM file")
    parser.add_argument("-p", "--partitions", required = True,
                        help = "Number of mesh partitions")
    args, _ = parser.parse_known_args(argv)

    mesh_file = args.mesh
    elmer_dir = args.elmer
    partitions = int(args.partitions)
    bed_file   = args.bed
    surf_file  = args.surface

    # Load in the Triangle mesh for the glacier
    xm, ym, ele, bnd = read_triangle_mesh(expanduser(mesh_file))
    tri = Triangulation(xm, ym, ele)
    nn = len(xm)

    print "Done reading Triangle mesh"

    # Get the basal friction parameter from Elmer
    beta = get_field("beta", elmer_dir, partitions, tri, surface = "bottom")

    # Get the computed basal and depth-averaged velocities
    ub = get_field("velocity 1", elmer_dir, partitions, tri, surface = "bottom")
    vb = get_field("velocity 2", elmer_dir, partitions, tri, surface = "bottom")

    uh = get_field("velocity 1", elmer_dir, partitions, tri, surface = "average")
    vh = get_field("velocity 2", elmer_dir, partitions, tri, surface = "average")

    print "Done getting Elmer output"

    # Compute the basal shear stress
    tau_b_x = np.zeros(nn, dtype = np.float64)
    tau_b_y = np.zeros(nn, dtype = np.float64)

    for i in range(nn):
        tau_b_x[i] = -beta[i]**2 * ub[i]
        tau_b_y[i] = -beta[i]**2 * vb[i]

    # Compute the driving stress
    xb, yb, bb = read_dem(bed_file)
    b = interpolate_grid_to_triangle(xb, yb, bb, tri)

    xs, ys, ss = read_dem(surf_file)
    s = interpolate_grid_to_triangle(xs, ys, ss, tri)

    # Compute the stresses
    basal_power   = basal_stress_power(tri, ub, vb, tau_b_x, tau_b_y)
    driving_power = driving_stress_power(tri, uh, vh, s, b)

    print basal_power / driving_power


if __name__ == "__main__":
    main(sys.argv[1:])
