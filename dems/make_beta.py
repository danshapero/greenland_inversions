#!/usr/bin/env python

import sys
sys.path.insert(0,'../scripts')

import os
import math
import numpy as np
from read_dem import *
from scipy import interpolate


year_in_sec = 365.25 * 24 * 60 * 60
rho = 917 * 1.0e-6 / year_in_sec**2
g = 9.81 * year_in_sec**2
A0 = 3.985e-13 * year_in_sec * 1.0e18
Q = 6.0e4
T = 273 - 13
R = 8.3144
A = A0 * math.exp(-Q / (R * T))


def compute_basal_fields(x, y, s, b, u, v):
    '''
    Inputs:
    x : list of horizontal coordinates of the grid
    y : list of vertical coordinates of the grid
    s : array of ice surface elevations
    b : array of ice bed elevations
    u : array of ice velocities in the x-direction
    v : array of ice velocities in the y-direction

    Outputs:
    beta : basal sliding coefficient, under the shallow ice approximation
    ub   : basal sliding velocity in the x-direction
    vb   : basal sliding velocity in the y-direction
    '''
    nx = len(x)
    ny = len(y)
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    #---------------------------
    # Compute the surface slope
    dsdx = np.zeros((ny, nx))
    dsdy = np.zeros((ny, nx))

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            dsdx[i, j] = 0.5 * (s[i, j + 1] - s[i, j - 1]) / dx
            dsdy[i, j] = 0.5 * (s[i + 1, j] - s[i - 1, j]) / dx


    #------------------------------------
    # Compute the bed sliding velocities
    ub = np.zeros((ny, nx))
    vb = np.zeros((ny, nx))

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            h = max(s[i, j] - b[i, j], 0.0)
            ds2 = dsdx[i, j]**2 + dsdy[i, j]**2
            rgh3 = (rho * g * h)**3
            ub[i, j] = u[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdx[i, j]
            vb[i, j] = v[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdy[i, j]

    sb = np.sqrt(ub**2 + vb**2)

    def fill_to_boundary(phi):
        phi[0, :] = phi[1, :]
        phi[-1, :] = phi[-2, :]
        phi[:, 0] = phi[:, 1]
        phi[:, -1] = phi[:, -2]

    fill_to_boundary(sb)
    fill_to_boundary(ub)
    fill_to_boundary(vb)


    #-------------------------------------
    # Compute the basal sliding parameter
    beta = np.zeros((ny, nx))
    for i in range(ny):
        for j in range(nx):
            h = max(s[i, j] - b[i, j], 0.0)
            dp = min(ub[i, j] * dsdx[i, j] + vb[i, j] * dsdy[i, j], 0.0)
            beta[i, j] = -rho * g * h * dp / (sb[i, j]**2 + 30.0)

    beta = np.sqrt(beta)

    for i in range(ny):
        for j in range(nx):
            beta[i, j] = max(beta[i, j], 0.0015)

    return beta, ub, vb



if __name__ == "__main__":
    glaciers = ["helheim", "kangerd", "jakobshavn"]

    for glacier in glaciers:
        if not os.path.exists(glacier + "/betaDEM.xy"):
            #--------------------------------------------
            # Read in the ice surface and bed elevations
            (x, y, s) = read_dem(glacier + "/zsDEM.xy")
            (x, y, b) = read_dem(glacier + "/zbDEM.xy")

            nx = len(x)
            ny = len(y)

            #----------------------------------
            # Smooth the ice surface elevation
            for i in range(1, ny - 1):
                for j in range(1, nx - 1):
                    s[i, j] = (4 * s[i, j] + s[i + 1, j] + s[i - 1, j]
                                            + s[i, j + 1] + s[i, j - 1]) / 8.0


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


            #----------------------------------------------
            # Compute some bed sliding velocities from SIA
            beta, ub, vb = compute_basal_fields(x, y, s, b, u, v)

            for i in range(ny):
                for j in range(nx):
                    ss = np.sqrt(u[i, j]**2 + v[i, j]**2)
                    sb = np.sqrt(ub[i, j]**2 + vb[i, j]**2)

                    if ss > 0:
                        ub[i, j] = u[i, j] * min(0.95, sb / ss)
                        vb[i, j] = v[i, j] * min(0.95, sb / ss)
                    else:
                        ub[i, j] = -2.0e+9
                        vb[i, j] = -2.0e+9


            fidbeta = open(glacier + "/betaDEM.xy", "w")
            fidbeta.write('{0}\n{1}\n'.format(nx, ny))

            for j in range(nx):
                for i in range(ny):
                    fidbeta.write('{0} {1} {2}\n'.format(x[j], y[i], beta[i, j]))


            print("Done computing basal fields for " + glacier)
