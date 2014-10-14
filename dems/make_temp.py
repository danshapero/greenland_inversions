#!/usr/bin/env python

import numpy as np
from scipy.interpolate import interp2d, griddata

import os
import sys
sys.path.insert(0, '../scripts')

from read_dem import *


def read_kristin_data(filename):
    """
    Read in Kristin's temperature/viscosity data.

    Inputs
    ------
    filename : the path to the input file

    Outputs
    -------
    X, Y : coordinates of the data points
    Z    : list of numpy arrays of the vertical coordinates in each column
    T    : list of numpy arrays of the temperature
    A    : list of numpy arrays of the fluidity
    """
    x = []
    y = []
    z = []
    t = []
    a = []

    # Read in the data from a file
    fid = open(filename, "r")
    line = fid.readline().split(',')
    line = fid.readline().split(',')

    while(line[0] != ""):
        x.append(float(line[0]))
        y.append(float(line[1]))
        z.append(float(line[2]))
        t.append(float(line[3]))
        a.append(float(line[4][:-1]))
        line = fid.readline().split(',')

    fid.close()

    # Condense the list so that all the temperature / viscosity from the same
    # (x, y)-point is contained in one list, and the data in a list of lists
    X = []
    Y = []
    Z = []
    T = []
    A = []

    X.append(x[0])
    Y.append(y[0])
    Z.append([z[0]])
    T.append([t[0]])
    A.append([a[0]])

    k = 0

    for n in range(1, len(x)):
        if x[n] == x[n - 1] and y[n] == y[n - 1]:
            Z[k].append(z[n])
            T[k].append(t[n])
            A[k].append(a[n])
        else:
            X.append(x[n])
            Y.append(y[n])
            Z.append([z[n]])
            T.append([t[n]])
            A.append([a[n]])
            k += 1

    nn = len(X)

    X = np.asarray(X)
    Y = np.asarray(Y)

    for k in range(nn):
        Z[k] = np.asarray(Z[k])
        T[k] = np.asarray(T[k])
        A[k] = np.asarray(A[k])

    return X, Y, Z, T, A



def low_pass_filter(q, iters):
    ny, nx = np.shape(q)

    def lpf(q):
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                q[i, j] = (4 * q[i, j] + q[i + 1, j] + q[i - 1, j]
                                        + q[i, j + 1] + q[i, j - 1]) / 8

    for k in range(iters):
        lpf(q)



#glaciers = ["helheim", "kangerd", "jakobshavn"]    # Need to get this from KP
glaciers = ["helheim", "kangerd"]


if __name__ == "__main__":
    for glacier in glaciers:
        outfile = glacier + "/ADEM.xy"
        if not os.path.exists(outfile):
            # Find the domain size for the current glacier
            x, y, vx = read_dem(glacier + "/UDEM.xy")

            ny, nx = np.shape(vx)
            mask = vx != -2.0e+9

            dx = x[1] - x[0]
            dy = y[1] - y[0]

            xmin = x[0]
            xmax = x[-1]
            ymin = y[0]
            ymax = y[-1]

            del vx

            # Read in Kristin's model output
            infile = "../data/" + glacier + "/xyzTA" + glacier + ".txt"
            X, Y, Z, T, A = read_kristin_data(infile)

            # Make a gridded data set from the model output
            # Set the number of vertical layers
            nz = 21
            a = np.zeros((ny, nx, nz))

            xg, yg = np.meshgrid(x, y)

            ak = np.zeros(len(X))
            for k in range(nz):
                for n in range(len(X)):
                    zmin = np.min(Z[n]) + 1.0e-2
                    zmax = np.max(Z[n]) - 1.0e-2
                    dz = (zmax - zmin) / (nz - 1)
                    z = zmin + k * dz
                    l = 0
                    while Z[n][l] > z:
                        l += 1
                    ak[n] = A[n][l] + (z - Z[n][l])/dz * A[n][l + 1]

                a[:, :, k] = griddata((X, Y), ak, (xg, yg), method = 'nearest')


            # Smooth over the gridded data
            for k in range(nz):
                low_pass_filter(a[:, :, k], 4)


            # Write the gridded data to a file
            fid = open(outfile, "w")
            fid.write("{0}\n{1}\n{2}\n".format(nx, ny, nz))

            for j in range(nx):
                for i in range(ny):
                    fid.write("{0} {1} ".format(x[j], y[i]))
                    for k in range(nz):
                        fid.write("{0} ".format(a[i, j, k]))
                    fid.write("\n")

            fid.close()

            print("Done computing flow law parameter for " + glacier)
