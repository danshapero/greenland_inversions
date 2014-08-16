import numpy as np

def write_to_qgis(filename,data,xllcorner,yllcorner,dx,no_data):
    fid = open(filename,'w')
    (ny,nx) = np.shape(data)

    fid.write('ncols         {0}\n'.format(nx))
    fid.write('nrows         {0}\n'.format(ny))
    fid.write('xllcorner     {0}\n'.format(xllcorner))
    fid.write('yllcorner     {0}\n'.format(yllcorner))
    fid.write('cellsize      {0}\n'.format(dx))
    fid.write('NODATA_value  {0}\n'.format(no_data))

    for i in range(ny-1,-1,-1):
        for j in range(nx):
            fid.write('{0} '.format(data[i,j]))
        fid.write('\n')

    fid.close()
