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


def compute_basal_fields(x, y, s, b, u, v, frac = 0.9):
    '''
    Inputs:
    x : list of horizontal coordinates of the grid
    y : list of vertical coordinates of the grid
    s : array of ice surface elevations
    b : array of ice bed elevations
    u : array of ice velocities in the x-direction
    v : array of ice velocities in the y-direction
    frac : optional parameter; the fraction of the driving stress that the
            basal shear stress is assumed to support

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


    #---------------------------------------------------------
    # Compute the bed sliding velocities & friction parameter
    ub = np.zeros((ny, nx))
    vb = np.zeros((ny, nx))
    beta = np.zeros((ny, nx))

    q = 0.0
    speed = 0.0

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            if u[i, j] != -2.0e+9:
                h = max(s[i, j] - b[i, j], 0.0)
                q = frac**3 * A * (rho * g * h)**3 * ds[i, j]**3 / 2
                speed = np.sqrt(u[i, j]**2 + v[i, j]**2)

                # The basal sliding velocities are assumed to have the same
                # direction as the surface velocities, only with lower speed
                # according to a rough SIA-like approximation.
                ub[i, j] = (speed - h*q) * u[i, j]/speed
                vb[i, j] = (speed - h*q) * v[i, j]/speed

                # Since we've already guessed the sliding speed and the
                # x-z strain rate from the SIA, the boundary condition
                #     tau_xz = -beta**2 * u    (resp. tau_yz, v)
                # gives us the value of beta consistent with the guesses
                # we've already made.
                beta[i, j] = (2*q / (A*(speed - h*q)**3))**(1.0/6)
            else:
                ub[i, j] = -2.0e+9
                vb[i, j] = -2.0e+9
                beta[i, j] = -2.0e+9


    def fill_to_boundary(phi):
        phi[0, :] = phi[1, :]
        phi[-1, :] = phi[-2, :]
        phi[:, 0] = phi[:, 1]
        phi[:, -1] = phi[:, -2]

    fill_to_boundary(beta)
    fill_to_boundary(ub)
    fill_to_boundary(vb)

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
            (xs, ys, sd) = read_dem(glacier + "/zsDEM.xy")
            (xb, yb, bd) = read_dem(glacier + "/zbDEM.xy")
            nxs = len(xs)
            nys = len(ys)


            #----------------------------------
            # Smooth the ice surface elevation
            for i in range(1, nys - 1):
                for j in range(1, nxs - 1):
                    sd[i, j] = (4 * sd[i, j] +
                                    sd[i + 1, j] + sd[i - 1, j] +
                                    sd[i, j + 1] + sd[i, j - 1]) / 8.0


            # Interpolate the elevation data to the grid for velocity
            sf = interpolate.RectBivariateSpline(xs, ys, sd.T)
            bf = interpolate.RectBivariateSpline(xb, yb, bd.T)
            s = np.zeros((ny, nx))
            b = np.zeros((ny, nx))

            for i in range(ny):
                for j in range(nx):
                    s[i, j] = sf(x[j], y[i])
                    b[i, j] = bf(x[j], y[i])

            del sf, bf, xs, ys, sd, xb, yb, bd


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
