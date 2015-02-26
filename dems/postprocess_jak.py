
import sys

import os
from scripts.read_dem import *


def relabel_external_missing_data(q, i, j):
    '''
    Relabel points of a gridded data set so that we can distinguish those
    that are truly missing data from those where we could interpolate from
    nearby points
    '''
    ny, nx = np.shape(q)

    stack = [ (i, j) ]
    q[i, j] = -3.0e+9

    while stack:
        (i, j) = stack.pop()
        q[i, j] = -4.0e+9

        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                k = (i + di) % ny
                l = (j + dj) % nx

                if q[k, l] == -2.0e+9:
                    q[k, l] = -3.0e+9
                    stack.append( (k, l) )


def fill_internal_missing_data(q, x, y, d):
    '''
    Fill in any missing data in the interior of the glacier, where it can be
    easily interpolated from surrounding points with data
    '''
    nx = len(x)
    ny = len(y)
    dx = x[1] - x[0]
    weight = 0.0

    I, J = np.where(q == -2.0e+9)
    nn = len(I)

    for m in range(nn):
        i = I[m]
        j = J[m]

        q[i, j] = 0.0

        weights = 0.0

        for di in range(-d, d+1):
            for dj in range(-d, d+1):
                k = i + di
                l = j + dj

                if q[k, l] > -2.0e+9 and not (i == k and j == l):
                    weight = 1.0 / np.sqrt(di**2 + dj**2)**3
                    q[i, j] += weight * q[k, l]
                    weights += weight

        if weights != 0.0:
            q[i, j] /= weights
        else:
            print("{0} {1}\n", i, j)


def fixup_data(filename, d, overwrite = True):
    x, y, q = read_dem(filename)

    nx = len(x)
    ny = len(y)

    qc = np.copy(q)
    relabel_external_missing_data(qc, 0, 0)
    fill_internal_missing_data(qc, x, y, d)
    q = np.maximum(qc, q)

    fid = open(filename + ".fixup", 'w')
    fid.write("{0}\n{1}\n".format(nx, ny))

    for j in range(nx):
        for i in range(ny):
            fid.write("{0} {1} {2}\n".format(x[j], y[i], q[i, j]))

    fid.close()

    if overwrite:
        os.system("mv " + filename + ".fixup " + filename)
