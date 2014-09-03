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

    qx = np.copy(vx)
    relabel_external_missing_data(qx, 0, 0)
    fill_internal_missing_data(qx, x, y)

    print(np.min(qx), np.max(qx))
