#!/usr/bin/env python

import sys
sys.path.insert(0, '../scripts')

import os
import math
import numpy as np
from scipy import interpolate

from read_dem import *
from write_qgis import *

rho = 917
g = 9.81

# ---------------------------------------------------------------------------- #
def driving_stress(x, y, s, b):                                                #
# ---------------------------------------------------------------------------- #
    '''
    Produce a gridded map of the driving stress of a glacier

    Parameters:
    ==========
    x, y: x- and y-coordinates of the DEMs
    s: 2d array of surface elevations
    b: 2d array of bed elevations

    Outputs:
    =======
    tau: driving stress, output on the same grid as the surface elevation
    '''

    nx = len(x)
    ny = len(y)

    dx = x[1] - x[0]
    dy = y[1] - y[0]

    h = 0.0
    dsdx = 0.0
    dsdy = 0.0

    tau = -9999.0 * np.ones((ny, nx))

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            dsdx = 0.5*(s[i, j+1] - s[i, j-1])/dx
            dsdy = 0.5*(s[i+1, j] - s[i-1, j])/dx

            h = max(s[i,j] - b[i,j], 0.0)

            # Factor of 1/1000 is because we want the result in kPa
            tau[i, j] = 1.0e-3 * rho*g*h*np.sqrt(dsdx**2 + dsdy**2)

    return tau


if __name__ == "__main__":
    glaciers = ["helheim", "kangerd", "jakobshavn"]

    for glacier in glaciers:
        # Read in the surface elevation
        (x, y, s) = read_dem(glacier + "/zsDEM.xy")
        nx = len(x)
        ny = len(y)

        # Smooth over the surface elevation
        s[1:ny-1, 1:nx-1] = (4*s[1:ny-1, 1:nx-1] 
                                + s[2:ny, 1:nx-1] + s[:ny-2, 1:nx-1]
                                + s[1:ny-1, 2:nx] + s[1:ny-1, :nx-2]) / 8

        # Read in the bed elevation
        (xb, yb, bd) = read_dem(glacier + "/zbDEM.xy")

        # Interpolate the bed elevation data to the surface elevation grid
        bf = interpolate.RectBivariateSpline(xb, yb, bd.T)
        b = np.zeros((ny, nx))

        for i in range(ny):
            for j in range(nx):
                b[i, j] = bf(x[j], y[i])

        del xb, yb, bd, bf

        # Make the driving stress field
        tau = driving_stress(x, y, s, b)

        # Output the driving stress field to QGIS's format
        write_to_qgis("../" + glacier + "_taud.txt",
                        tau, x[0], y[0], x[1] - x[0], -9999.0)

        print("Done writing driving stress for " + glacier)

