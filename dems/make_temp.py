#!/usr/bin/env python

import numpy as np

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
    x, y, z : coordinates of the data poins
    T       : numpy array of modelled temperature values at each data point
    A       : numpy array of the viscosity at each point
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

    X.append([x[0]])
    Y.append([y[0]])
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
            X.append([x[n]])
            Y.append([y[n]])
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




glaciers = ["helheim", "kangerd", "jakobshavn"]


if __name__ == "__main__":
    for glacier in glaciers:
        outfile = glacier + "/ADEM.xy"
        if not os.path.exists(outfile):
            # Find the domain size for the current glacier
            x, y, vx = read_dem(glacier + "/UDEM.xy")

            ny, nx = np.shape(vx)

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


