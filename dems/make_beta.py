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

    # Compute the magnitude of the surface slope, the average slope and the 
    # standard deviation of the slope
    ds = np.sqrt(dsdx**2 + dsdy**2)
    avg = np.average(ds)
    stddev = np.std(ds)

    # The maximum slope we'll allow, for the purposes of coming up with a
    # bed sliding velocity, is the average + 1 standard deviation.
    mva = avg + 0.25 * stddev

    # Scale the surface slope at any point where it's too steep
    for i in range(ny):
        for j in range(nx):
            if ds[i, j] > mva:
                dsdx[i, j] = mva / ds[i, j] * dsdx[i, j]
                dsdy[i, j] = mva / ds[i, j] * dsdy[i, j]
                ds[i, j] = mva


    #------------------------------------
    # Compute the bed sliding velocities
    ub = np.zeros((ny, nx))
    vb = np.zeros((ny, nx))

    # First use SIA to get a rough estimate of the bed sliding velocity
    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            if u[i, j] != -2.0e+9:
                h = max(s[i, j] - b[i, j], 0.0)
                ds2 = ds[i, j]**2
                rgh3 = (rho * g * h)**3
                ub[i, j] = u[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdx[i, j]
                vb[i, j] = v[i, j] + 0.5 * A * rgh3 * h * ds2 * dsdy[i, j]
            else:
                ub[i, j] = -2.0e+9
                vb[i, j] = -2.0e+9

    # The SIA guess could behave very pathologically in some places, so force
    # the bed velocities to point in the same direction as the surface
    # velocities and cut off the speeds at some minimum / maximum
    for i in range(ny):
        for j in range(nx):
            if u[i, j] != -2.0e+9:
                ss = np.sqrt(u[i, j]**2 + v[i, j]**2)
                sb = np.sqrt(ub[i, j]**2 + vb[i, j]**2)

                angle = 1.0
                if ss > 0 and sb > 0:
                    angle = (u[i, j]*ub[i, j] + v[i, j]*vb[i, j]) / (ss * sb)

                ub[i, j] = u[i, j] * min(0.99, sb / ss) * max(angle, 0.05)
                vb[i, j] = v[i, j] * min(0.99, sb / ss) * max(angle, 0.05)

    def fill_to_boundary(phi):
        phi[0, :] = phi[1, :]
        phi[-1, :] = phi[-2, :]
        phi[:, 0] = phi[:, 1]
        phi[:, -1] = phi[:, -2]

    fill_to_boundary(ub)
    fill_to_boundary(vb)


    #-------------------------------------
    # Compute the basal sliding parameter

    # Chooe some fraction of the driving stress for the basal shear stress
    # to support
    frac = 0.9

    # beta = stress / speed
    beta = np.zeros((ny, nx))
    for i in range(ny):
        for j in range(nx):
            if u[i, j] != -2.0e+9:
                h = max(s[i, j] - b[i, j], 0.0)
                dp = min(ub[i, j] * dsdx[i, j] + vb[i, j] * dsdy[i, j], 0.0)
                sb = np.sqrt(ub[i, j]**2 + vb[i, j]**2)
                beta[i, j] = -frac * rho * g * h * dp / (sb**2 + 30.0)

    beta = np.sqrt(beta)

    for i in range(ny):
        for j in range(nx):
            if u[i, j] == -2.0e+9:
                beta[i, j] = -2.0e+9

    return beta, ub, vb



if __name__ == "__main__":
    glaciers = ["helheim", "kangerd", "jakobshavn"]

    for glacier in glaciers:
        if not (os.path.exists(glacier + "/betaDEM.xy")
            and os.path.exists(glacier + "/UBDEM.xy"  )
            and os.path.exists(glacier + "/VBDEM.xy"  )):
            #------------------------------------
            # Read in the ice surface velocities
            (x, y, u) = read_dem(glacier + "/UDEM.xy")
            (x, y, v) = read_dem(glacier + "/VDEM.xy")

            nx = len(x)
            ny = len(y)


            #--------------------------------------------
            # Read in the ice surface and bed elevations
            (xd, yd, sd) = read_dem(glacier + "/zsDEM.xy")
            (xd, yd, bd) = read_dem(glacier + "/zbDEM.xy")
            nxd = len(xd)
            nyd = len(yd)


            #----------------------------------
            # Smooth the ice surface elevation
            for i in range(1, nyd - 1):
                for j in range(1, nxd - 1):
                    sd[i, j] = (4 * sd[i, j] +
                                    sd[i + 1, j] + sd[i - 1, j] +
                                    sd[i, j + 1] + sd[i, j - 1]) / 8.0


            # Interpolate the elevation data to the grid for velocity
            sf = interpolate.RectBivariateSpline(xd, yd, sd.T)
            bf = interpolate.RectBivariateSpline(xd, yd, bd.T)
            s = np.zeros((ny, nx))
            b = np.zeros((ny, nx))

            for i in range(ny):
                for j in range(nx):
                    s[i, j] = sf(x[j], y[i])
                    b[i, j] = bf(x[j], y[i])

            del sf, bf, xd, yd, sd, bd


            #----------------------------------------------
            # Compute some bed sliding velocities from SIA
            beta, ub, vb = compute_basal_fields(x, y, s, b, u, v)

            for i in range(ny):
                for j in range(nx):
                    if beta[i, j] != -2.0e+9:
                        beta[i, j] = max(beta[i, j], 0.015)


            #---------------------------------
            # Write the results out to a file
            fidbeta = open(glacier + "/betaDEM.xy", "w")
            fidub   = open(glacier + "/UBDEM.xy", "w")
            fidvb   = open(glacier + "/VBDEM.xy", "w")
            fidbeta.write('{0}\n{1}\n'.format(nx, ny))
            fidub.write('{0}\n{1}\n'.format(nx, ny))
            fidvb.write('{0}\n{1}\n'.format(nx, ny))

            for j in range(nx):
                for i in range(ny):
                    fidbeta.write("{0} {1} {2}\n".format(x[j], y[i], beta[i, j]))
                    fidub.write("{0} {1} {2}\n".format(x[j], y[i], ub[i, j]))
                    fidvb.write("{0} {1} {2}\n".format(x[j], y[i], vb[i, j]))

            fidbeta.close()
            fidub.close()
            fidvb.close()


            print("Done computing basal fields for " + glacier)
