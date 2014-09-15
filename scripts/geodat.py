import numpy as np
from scipy.io import *
import struct
import sys
import math

# This function reads the .geodat file, which stores the number of pixels
# in the image, the pixel size and the location of the lower left corner
def readgeodat(filename):
    geodatfile = open(filename,"r")
    xgeo = np.zeros((3,2))
    i = 0
    while True:
        line = geodatfile.readline().split()
        if len(line)==2:
            try:
                xgeo[i,0] = float(line[0])
                xgeo[i,1] = float(line[1])
                i = i+1
            except ValueError:
                i = i
        if len(line)==0:
            break
    geodatfile.close()
    xgeo[2,:] = xgeo[2,:]*1000.0
    return xgeo


def readvelocity(filename):
    # Get the data about the grid from the .geodat file
    xgeo = readgeodat(filename+".vx.geodat")
    (nx, ny) = (int(xgeo[0,0]), int(xgeo[0,1]))
    (dx, dy) = (xgeo[1,0], xgeo[1,1])
    (xo, yo) = (xgeo[2,0], xgeo[2,1])
    x = np.zeros(nx)
    for i in range(nx):
        x[i] = xo+i*dx
    y = np.zeros(ny)
    for i in range(ny):
        y[i] = yo+i*dy

    # Open the x-velocity file and read in all the binary data
    vxfile = open(filename+".vx","rb")
    vx_raw_data = vxfile.read()
    vxfile.close()

    # Unpack that binary data to an array of floats, knowing that it is
    # in big-endian format. Why? God only knows.
    nvals = len(vx_raw_data)/4
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f',vx_raw_data[4*i:4*(i+1)])[0]

    # Fairly certain that this is right, but plot it and compare against
    # matlab to be certain
    vx = arr.reshape((ny,nx))

    # Go through the same rigmarole for the y-velocity file
    vyfile = open(filename+".vy","rb")
    vy_raw_data = vyfile.read()
    vyfile.close()
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f',vy_raw_data[4*i:4*(i+1)])[0]
    vy = arr.reshape((ny,nx))

    # Do the same thing for the files containing the errors
    exfile = open(filename+".ex","rb")
    ex_raw_data = exfile.read()
    exfile.close()
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f',ex_raw_data[4*i:4*(i+1)])[0]
    ex = arr.reshape((ny,nx))

    eyfile = open(filename+".ey","rb")
    ey_raw_data = eyfile.read()
    eyfile.close()
    arr = np.zeros(nvals)
    for i in range(nvals):
        arr[i] = struct.unpack('>f',ey_raw_data[4*i:4*(i+1)])[0]
    ey = arr.reshape((ny,nx))

    # Find weird points. For example, a point with no data but which has
    # four cardinal neighbors (N,S,E,W) that does can reasonably have data
    # there, interpolated from its cardinal neighbors. Likewise, a point
    # which does have data but for which only 2 of its 8 neighbors (N,S,E,W,
    # NW,NE,SE,SW) have data would be better off ignored.
    for i in range(1,ny-1):
        for j in range(1,nx-1):
            if (vx[i,j]==-2e+9):
                nbrs = [ [i+1,i-1,i,i], [j,j,j+1,j-1] ]
                k = sum( vx[nbrs[0],nbrs[1]]!=-2e+9 )
                if (k==4):
                    vx[i,j] = sum( vx[nbrs[0],nbrs[1]] )/4.0
                    vy[i,j] = sum( vy[nbrs[0],nbrs[1]] )/4.0
            else:
                nbrs = [ [i+1,i+1,i+1,i,i,i-1,i-1,i-1], [j+1,j,j-1,j+1,j-1,j+1,j,j-1] ]
                k = sum( vx[nbrs[0],nbrs[1]]!=-2e+9 )
                if (k<2):
                    vx[i,j] = -2e+9
                    vy[i,j] = -2e+9

    for i in range(1,ny-1):
        for j in range(1,nx-1):
            if (vx[i,j]!=-2e+9):
                nbrs = [ [i+1,i+1,i+1,i,i,i-1,i-1,i-1], [j+1,j,j-1,j+1,j-1,j+1,j,j-1] ]
                k = sum( vx[nbrs[0],nbrs[1]]!=-2e+9 )
                if (k<4):
                    vx[i,j] = -2e+9
                    vy[i,j] = -2e+9

    return (x,y,vx,vy,ex,ey)

