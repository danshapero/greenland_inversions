import numpy as np
from scipy.io import *
import struct
import sys
import math


def read_geodat(filename):

    def _read_geodat(filename):
        # read in the .geodat file, which stores the number of pixels,
        # the pixel size and the location of the lower left corner
        geodatfile = open(filename, "r")
        xgeo = np.zeros((3,2))
        i = 0
        while True:
            line = geodatfile.readline().split()
            if len(line) == 2:
                try:
                    xgeo[i, 0] = float(line[0])
                    xgeo[i, 1] = float(line[1])
                    i += 1
                except ValueError:
                    i = i
            if len(line) == 0:
                break
        geodatfile.close()
        xgeo[2,:] = xgeo[2,:] * 1000.0
        return xgeo

    # Get the data about the grid from the .geodat file
    xgeo = _read_geodat(filename + ".geodat")
    nx, ny = map(int, xgeo[0,:])
    dx, dy = xgeo[1,:]
    xo, yo = xgeo[2,:]
    x = np.zeros(nx)
    for i in range(nx):
        x[i] = xo + i * dx
    y = np.zeros(ny)
    for i in range(ny):
        y[i] = yo + i * dy

    # Open the x-velocity file and read in all the binary data
    data_file = open(filename, "rb")
    raw_data = data_file.read()
    data_file.close()

    # Unpack that binary data to an array of floats, knowing that it is
    # in big-endian format. Why? God only knows.
    nvals = len(raw_data)/4
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f', raw_data[4*i: 4*(i+1)])[0]

    # Fairly certain that this is right, but plot it and compare against
    # matlab to be certain
    data = arr.reshape((ny, nx))

    # Find weird points.
    if np.min(data) == -2.0e+9:
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                # A point with no data but which has four cardinal neighbors
                # that does can rasonably have data interpolated from them
                if data[i, j] == -2e+9:
                    nbrs = [ [i+1, i-1, i,   i  ],
                             [j,   j,   j+1, j-1] ]
                    k = sum( data[nbrs[0], nbrs[1]] != -2e+9 )
                    if k == 4:
                        data[i,j] = sum( data[nbrs[0],nbrs[1]] )/4.0

                # A point which does have data but for which only one of its
                # neighbors neighbors does should not have data
                else:
                    nbrs = [ [i+1, i+1, i+1, i,   i,   i-1, i-1, i-1],
                             [j+1, j,   j-1, j+1, j-1, j+1, j,   j-1] ]
                    k = sum( data[nbrs[0],nbrs[1]]!=-2e+9 )
                    if k <= 1:
                        data[i,j] = -2e+9
                        data[i,j] = -2e+9

        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                if data[i,j] != -2e+9:
                    nbrs = [ [i+1, i+1, i+1, i,   i,   i-1, i-1, i-1],
                             [j+1, j,   j-1, j+1, j-1, j+1, j,   j-1] ]
                    k = sum( data[nbrs[0], nbrs[1]] != -2e+9 )
                    if k < 4:
                        data[i,j] = -2e+9
                        data[i,j] = -2e+9

    return x, y, data

