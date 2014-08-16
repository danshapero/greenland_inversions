import numpy as np

def read_dem(filename):
    fid = open(filename,'r')

    nx = int(fid.readline().split()[0])
    ny = int(fid.readline().split()[0])

    x = np.zeros(nx)
    y = np.zeros(ny)

    q = np.zeros((ny,nx))

    for j in range(nx):
        for i in range(ny):
            (x[j],y[i],q[i,j]) = map(float,fid.readline().split())

    return x,y,q
