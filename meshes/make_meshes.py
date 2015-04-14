#!/usr/bin/env python

import sys
import argparse
import os

import numpy as np
from scripts.meshes import *


# -------------
def main(argv):
    # Parse command-line arguments
    dx = 250

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--length", required = False,
                        help = "")
    args, _ = parser.parse_known_args(argv)
    if args.length:
        dx = float(args.length)

    glaciers = ["helheim", "kangerd", "jakobshavn"]

    for glacier in glaciers:
        filename = glacier + '/' + glacier

        # Generate a preliminary mesh
        if not os.path.exists(filename + ".1.node"):
            os.system("triangle -pqnea250000.0 " + filename + ".poly")

        # Make a .area file to inform the triangulation of a finer mesh
        if not os.path.exists(filename + '.1.area'):
            # Read the velocities
            fid = open("../dems/" + glacier + "/UDEM.xy")
            nx = int(fid.readline().split()[0])
            ny = int(fid.readline().split()[0])

            vx = np.zeros((ny, nx))
            X = np.zeros(nx)
            Y = np.zeros(ny)

            for j in range(nx):
                for i in range(ny):
                    X[j], Y[i], vx[i,j] = map(float, fid.readline().split()[0:])

            fid.close()

            fid = open("../dems/" + glacier + "/VDEM.xy")
            nx = int(fid.readline().split()[0])
            ny = int(fid.readline().split()[0])

            vy = np.zeros((ny, nx))
            for j in range(nx):
                for i in range(ny):
                    X[j], Y[i], vy[i,j] = map(float, fid.readline().split()[0:])
            fid.close()

            # Compute the speed
            V = np.zeros((ny, nx))
            for i in range(ny):
                for j in range(nx):
                    if vx[i,j] != -2e+9:
                        V[i,j] = np.sqrt(vx[i,j]**2 + vy[i,j]**2)

            del vx, vy

            # Load in the preliminary mesh
            x, y, ele, bnd = read_triangle_mesh(filename + ".1")

            ne = np.shape(ele)[0]
            nn = len(x)

            # Find the ice speed at all the mesh points
            v = np.zeros(nn)
            for n in range(nn):
                i = int( (y[n] - Y[0]) / 100.0 )
                j = int( (x[n] - X[0]) / 100.0 )
                v[n] = 0.25*(V[i,j] + V[i+1,j] + V[i,j+1] + V[i+1,j+1])

            del V, X, Y

            # Output the .area file
            area = np.zeros(ne)
            for n in range(ne):
                speed = sum(v[ele[n,:]])/3
                if (speed > 1000.0):
                    area[n] = np.sqrt(3) / 4 * dx**2
                elif (speed > 500.0):
                    area[n] = np.sqrt(3) / 4 * (2*dx)**2
                else:
                    area[n] = np.sqrt(3) / 4 * (4*dx)**2

            fid = open(filename + ".1.area", 'w')
            fid.write('{0}\n'.format(ne))
            for n in range(ne-1):
                fid.write('{0} {1}\n'.format(n+1, area[n]))
            fid.write('{0} {1}'.format(ne, area[ne-1]))
            fid.close()

        # Generate the refined mesh
        if not os.path.exists(filename + '.2.node'):
            os.system('triangle -rpqnea ' + filename+'.1')


# ---------------------------------------------------------------------------- #
if __name__ == "__main__":                                                     #
# ---------------------------------------------------------------------------- #
    main(sys.argv[1:])

