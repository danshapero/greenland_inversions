#!/usr/bin/env python

import sys
sys.path.insert(0,'../scripts')

import math
import numpy as np
from read_dem import *
from scipy import interpolate


year_in_sec = 365.25 * 24 * 60 * 60
rho = 917 * 1.0e-6 / year_in_sec**2
g = -9.81 * year_in_sec**2
A0 = 3.985e-13 * year_in_sec * 1.0e18
Q = 6.0e4
T = 273 - 13
R = 8.3144
A = A0 * math.exp(-Q / (R * T))


glaciers = ["helheim", "kangerd", "jakobshavn"]

for glacier in glaciers:
    #--------------------------------------------
    # Read in the ice surface and bed elevations
    (x, y, s) = read_dem(glacier + "/zsDEM.xy")
    (x, y, b) = read_dem(glacier + "/zbDEM.xy")

    nx = len(x)
    ny = len(y)
    dx = x[1] - x[0]
    dy = y[1] - y[0]


    #------------------------------------
    # Read in the ice surface velocities
    (xr, yr, ur) = read_dem(glacier + "/UDEM.xy")
    (xr, yr, vr) = read_dem(glacier + "/VDEM.xy")

    nxr = len(xr)
    nyr = len(yr)

    for i in range(nyr):
        for j in range(nxr):
            if ur[i, j] == -2.0e+9:
                ur[i, j] = 0.0
                vr[i, j] = 0.0

    # Interpolate the velocity data to the grid for the elevations    
    uf = interpolate.RectBivariateSpline(xr, yr, ur.T)
    vf = interpolate.RectBivariateSpline(xr, yr, vr.T)
    u = np.zeros((ny, nx))
    v = np.zeros((ny, nx))
    for i in range(ny):
        for j in range(nx):
            u[i, j] = uf(x[j], y[i])
            v[i, j] = vf(x[j], y[i])

    del uf, vf, xr, yr, ur, vr


    #---------------------------
    # Compute the surface slope
    dsdx = np.zeros((ny, nx))
    dsdy = np.zeros((ny, nx))

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            dsdx[i, j] = 0.5 * (s[i, j + 1] - s[i, j - 1]) / dx
            dsdy[i, j] = 0.5 * (s[i + 1, j] - s[i - 1, j]) / dx


    ub = np.zeros((ny, nx))
    vb = np.zeros((ny, nx))


    #------------------------------------
    # Compute the bed sliding velocities
    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            h = s[i, j] - b[i, j]
            ds2 = dsdx[i, j]**2 + dsdy[i, j]**2
            rgh3 = (rho * g * h)**3
            ub[i, j] = u[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdx[i, j]
            vb[i, j] = v[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdy[i, j]

    sb = np.sqrt(ub**2 + vb**2)
    print("{0} {1}\n".format(np.min(sb), np.max(sb)))

