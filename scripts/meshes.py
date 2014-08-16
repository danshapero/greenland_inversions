from geodat import *
import math
from scipy.sparse import lil_matrix



############################################################################
# Function to read in .poly files                                          #
############################################################################
def read_poly(filename):
    fid = open(filename,'r')

    # Read in the coordinates of the boundary pointers
    nn = int(fid.readline().split()[0])

    x = np.zeros(nn)
    y = np.zeros(nn)
    bnd = np.zeros(nn,dtype=np.int)
    for i in range(nn):
        line = fid.readline().split()
        x[i] = float(line[1])
        y[i] = float(line[2])
        bnd[i] = int(line[3])

    # Read in the edges
    ne = int(fid.readline().split()[0])

    edge = np.zeros((ne,2),dtype=np.int)
    for i in range(nn):
        line = fid.readline().split()
        edge[i,0] = int(line[1])-1
        edge[i,1] = int(line[2])-1

    # Read in the holes
    nh = int(fid.readline().split()[0])

    xh = np.zeros(nh)
    yh = np.zeros(nh)
    for i in range(nh):
        line = fid.readline().split()
        xh[i] = float(line[1])
        yh[i] = float(line[2])

    return(x,y,bnd,edge,xh,yh)    


############################################################################
# Function to read meshes stored in Triangle's file format                 #
############################################################################
def read_triangle_mesh(filename):
    fid = open(filename+".node","r")
    nn = int( fid.readline().split()[0] )
    x = np.zeros(nn)
    y = np.zeros(nn)
    bnd = np.zeros(nn,dtype=np.int)
    for i in range(nn):
        line = fid.readline().split()
        x[i] = float(line[1])
        y[i] = float(line[2])
        bnd[i] = int(line[3])
    fid.close()

    fid = open(filename+".ele","r")
    ne = int( fid.readline().split()[0] )
    ele = np.zeros((ne,3),dtype=int)
    for i in range(ne):
        ele[i,:] = map(int,fid.readline().split()[1:])
        ele[i,:] = ele[i,:]-np.ones(3)
    fid.close()

    return (x,y,ele,bnd)


