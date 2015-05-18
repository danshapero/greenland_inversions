from geodat import *
import math


# ------------
def area(x, y):
    return 0.5 * np.abs((x[1] - x[0]) * (y[2] - y[0]) -
                        (x[2] - x[0]) * (y[1] - y[0]))


# -----------------------------------------
def gridded_to_point_cloud(x, y, xq, yq, q):
    """
    Interpolate gridded data to a point cloud

    Arguments
    =========
    x, y:   coordinates of the point cloud
    xq, yq: positions of the regular grid
    q:      gridded data set

    Returns:
    =======
    r: gridded data set, interpolated to x, y
    """

    nn = len(x)
    r = np.zeros(nn, dtype = np.float64)

    dx = xq[1] - xq[0]
    dy = yq[1] - yq[0]

    for k in range(nn):
        i = int( (y[k] - yq[0]) / dy )
        j = int( (x[k] - xq[0]) / dx )

        ay = (y[k] - yq[i]) / dy
        ax = (x[k] - xq[j]) / dx

        r[k] = (q[i, j] + ax*(q[i, j+1] - q[i, j])
                        + ay*(q[i+1, j] - q[i, j])
                        + ax*ay*(q[i, j] + q[i+1, j+1] - q[i, j+1] - q[i+1, j]))

    return r


# ---------------------
def read_poly(filename):
    """
    Read in a .poly file in Triangle's format.

    Arguments
    =========
    filename: string
        path to the .poly file

    Returns
    =======
    x, y : numpy array of doubles
        coordinates of the points of the planar straight-line graph (PSLG)
    bnd : numpy array of ints
        boundary markers
    edge : numpy array of ints
        list of edges of the PSLG
    xh, yh : numpy array of doubles
        coordinates of holes
    """
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

    return x, y, bnd, edge, xh, yh


# ------------------------------
def read_triangle_mesh(filename):
    """
    Function to read in an unstructured grid in Triangle's format.

    Arguments
    =========
    filename: stem for the Triangle files, e.g. for the triangulation stored
              in the files {path/my_tri.node, path/my_tri.ele, ...}, this
              would be `path/my_tri`.

    Returns
    =======
    x, y: coordinates of the triangulation
    ele:  indices of each triangle
    bnd:  boundary indicators for each vertex
    """
    fid = open(filename + ".node", "r")
    nn = int( fid.readline().split()[0] )
    x = np.zeros(nn)
    y = np.zeros(nn)
    bnd = np.zeros(nn, dtype = np.int32)
    for i in range(nn):
        line = fid.readline().split()
        x[i] = float(line[1])
        y[i] = float(line[2])
        bnd[i] = int(line[3])
    fid.close()

    fid = open(filename + ".ele", "r")
    ne = int( fid.readline().split()[0] )
    ele = np.zeros((ne, 3), dtype=np.int32)
    for i in range(ne):
        ele[i,:] = map(int, fid.readline().split()[1:])
        ele[i,:] = ele[i,:] - np.ones(3)
    fid.close()

    return x, y, ele, bnd
