#!/usr/bin/env python

import sys
sys.path.insert(0, '../scripts')

import os
from read_dem import *


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


def fill_internal_missing_data(q, x, y):
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

        for di in range(-3, 4):
            for dj in range(-3, 4):
                k = i + di
                l = j + dj

                if q[k, l] > -2.0e+9 and not (i == k and j == l):
                    weight = 1.0 / np.sqrt(di**2 + dj**2)**3
                    q[i, j] += weight * q[k, l]
                    weights += weight

        if weights != 0.0:
            q[i, j] /= weights
            print (i, j, q[i, j])
        else:
            print("{0} {1}\n", i, j)


if __name__ == "__main__":
    (x, y, vx) = read_dem('jakobshavn/UDEM.xy')
    (x, y, vy) = read_dem('jakobshavn/VDEM.xy')

    nx = len(x)
    ny = len(y)

    q = np.copy(vx)
    relabel_external_missing_data(q, 0, 0)
    fill_internal_missing_data(q, x, y)
    vx = np.maximum(q, vx)

    q = np.copy(vy)
    relabel_external_missing_data(q, 0, 0)
    fill_internal_missing_data(q, x, y)
    vy = np.maximum(q, vy)

    fidu = open('jakobshavn/UDEM0.xy', 'w')
    fidv = open('jakobshavn/VDEM0.xy', 'w')

    for fid in (fidu, fidv):
        fid.write("{0}\n{1}\n".format(nx, ny))

    for j in range(nx):
        for i in range(ny):
            fidu.write("{0} {1} {2}\n".format(x[j], y[i], vx[i, j]))
            fidv.write("{0} {1} {2}\n".format(x[j], y[i], vy[i, j]))

    for fid in (fidu, fidv):
        fid.close()

    os.system("mv jakobshavn/UDEM0.xy jakobshavn/UDEM.xy")
    os.system("mv jakobshavn/VDEM0.xy jakobshavn/VDEM.xy")

