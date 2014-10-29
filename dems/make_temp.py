#!/usr/bin/env python

import numpy as np
from scipy.spatial import cKDTree

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
        outfile = glacier + "/TDEM.xy"
        if not os.path.exists(outfile):
            # ---------------------------------------------
            # Find the domain size for the current glacier
            x, y, vx = read_dem(glacier + "/UDEM.xy")

            ny, nx = np.shape(vx)
            del vx

            dx = x[1] - x[0]
            dy = y[1] - y[0]

            xmin = x[0]
            xmax = x[-1]
            ymin = y[0]
            ymax = y[-1]

            # -------------------------------
            # Read in Kristin's model output
            infile = "../data/" + glacier + "/xyzTA" + glacier + ".txt"
            X, Y, Z, T, A = read_kristin_data(infile)

            # Set the number of vertical layers
            nz = 21

            # Make the default temperature -10C
            temp = 263 * np.ones((ny, nx, nz))
            mask = np.zeros((ny, nx), dtype = bool)


            # ----------------------------------------------
            # Make a gridded data set from the model output

            pts = np.zeros((len(X), 2))
            pts[:,0] = X
            pts[:,1] = Y

            # Make a KD-tree so we can do range searches fast
            tree = cKDTree(pts)

            # For each point in the grid,
            for i in range(ny):
                for j in range(nx):
                    # find all the model points within 1km of it.
                    L = tree.query_ball_point( (x[j], y[i]), 1000 )

                    # Initialize the weights to 1; if there aren't any
                    # other nearby model points to interpolate from, we'll
                    # keep the temperature value at -10C
                    weights = 1.0

                    # For all the nearby model points,
                    for l in L:
                        xp = X[l]
                        yp = Y[l]

                        # find the distance to the current point and the
                        # appropriate weight
                        r = np.sqrt( (x[j] - xp)**2 + (y[i] - yp)**2 )
                        w = (1000/(r+dx))**3
                        weights += w

                        # For each point within the current vertical column,
                        for k in range(nz):
                            # find which point within the nearby vertical
                            # column to interpolate from
                            m = (k * (len(Z[l]) - 1)) / (nz - 1)

                            # Add up the value to the running average
                            temp[i, j, k] += w * T[l][m]

                    # Normalize the running average by the weight sum
                    temp[i,j,:] /= weights


            # ---------------------------------
            # Write the gridded data to a file
            fid = open(outfile, "w")
            fid.write("{0}\n{1}\n{2}\n".format(nx, ny, nz))

            for j in range(nx):
                for i in range(ny):
                    fid.write("{0} {1} ".format(x[j], y[i]))
                    for k in range(nz):
                        fid.write("{0} ".format(temp[i, j, k]))
                    fid.write("\n")

            fid.close()

            print("Done computing flow law parameter for " + glacier)
