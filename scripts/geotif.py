from osgeo import gdal
import numpy as np
import math

'''
Script to read geotif files
'''

def readgeotif(filename,xmin=-np.Inf,xmax=np.Inf,ymin=-np.Inf,ymax=np.Inf):
    geotiffile = gdal.Open(filename,gdal.GA_ReadOnly)

    # Get the size of the dataset
    nx = geotiffile.RasterXSize
    ny = geotiffile.RasterYSize

    # Load the data from the file
    z = np.zeros((ny,nx))
    z = geotiffile.GetRasterBand(1).ReadAsArray()
    z = z[::-1,:]

    # Get the coordinates of the image
    gt = geotiffile.GetGeoTransform()
    x = np.zeros(nx)
    y = np.zeros(ny)
    for i in range(nx):
        x[i] = gt[0]+i*gt[1]
    for i in range(ny):
        y[i] = gt[3]+i*gt[5]
    y = y[::-1]

    dx = math.fabs(gt[1])
    dy = math.fabs(gt[5])

    j0 = int( max(  0, (xmin-x[0])/dx )   )
    j1 = int( min( nx, (xmax-x[0])/dx )+1 )
    i0 = int( max(  0, (ymin-y[0])/dy )   )
    i1 = int( min( ny, (ymax-y[0])/dy )+1 )


    return (x[j0:j1],y[i0:i1],z[i0:i1,j0:j1])
