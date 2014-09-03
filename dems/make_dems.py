#!/usr/bin/env python

import sys
sys.path.insert(0,'../scripts')

import os
from geodat import *
from geotif import *
from read_dem import *

filenames = {
                'helheim':  {
                    'velocity': 'TSX_E66.50N_27Jan09_07Feb09',
                    'surface' : 'zsDEM.xy',
                    'bed'     : 'zbDEM.xy'
                },

                'kangerd': {
                    'velocity': 'TSX_E68.80N_28Jan09_08Feb09',
                    'surface' : 'zsDEM.xy',
                    'bed'     : 'zbDEM.xy'
                },

                 'jakobshavn': {
                     'velocity': 'mosaicOffsets',
                     'surface' : 'zsDEM.xy',
                     'bed'     : 'zbDEM.xy'
                 }
            }



for glacier in filenames.keys():
    if not os.path.exists(glacier):
        os.makedirs(glacier)

    ########################################################################
    ## Make velocity data files                                           ##
    ########################################################################
    # Check to see if the velocity DEMs have already been made
    if not( os.path.exists(glacier+'/UDEM.xy') or
            os.path.exists(glacier+'/VDEM.xy') or
            os.path.exists(glacier+'/EUDEM.xy') or
            os.path.exists(glacier+'/EVDEM.xy')):
        # Read in the velocity data files
        filename = '../data/'+glacier+'/'+filenames[glacier]['velocity']
        (x,y,vx,vy,ex,ey) = readvelocity(filename)

        # Find the points where there actually is measured velocity data
        (I,J) = np.where(vx!=-2.0e+9)
        (imin,imax) = (min(I)-2,max(I)+2)
        (jmin,jmax) = (min(J)-2,max(J)+2)
        del I,J

        vx = vx[imin:imax+1,jmin:jmax+1]
        vy = vy[imin:imax+1,jmin:jmax+1]
        ex = ex[imin:imax+1,jmin:jmax+1]
        ey = ey[imin:imax+1,jmin:jmax+1]

        x = x[jmin:jmax+1]
        y = y[imin:imax+1]
        nx = jmax-jmin+1
        ny = imax-imin+1

        # Write out the velocity data
        fidu = open(glacier+'/UDEM.xy','w')
        fidv = open(glacier+'/VDEM.xy','w')
        fideu = open(glacier+'/EUDEM.xy','w')
        fidev = open(glacier+'/EVDEM.xy','w')

        for fid in [fidu, fidv, fideu, fidev]:
            fid.write('{0}\n{1}\n'.format(nx,ny))

        for j in range(nx):
            for i in range(ny):
                fidu.write('{0} {1} {2}\n'.format(x[j],y[i],vx[i,j]))
                fidv.write('{0} {1} {2}\n'.format(x[j],y[i],vy[i,j]))
                fideu.write('{0} {1} {2}\n'.format(x[j],y[i],ex[i,j]))
                fidev.write('{0} {1} {2}\n'.format(x[j],y[i],ey[i,j]))

        for fid in [fidu, fidv, fideu, fidev]:
            fid.close()

        # Delete the velocities
        del vx, vy, ex, ey


    ########################################################################
    ## Fetch surface and bed DEMs                                         ##
    ########################################################################
    # Check whether or not the be DEM has already been made
    files = ["zbDEM.xy", "zsDEM.xy"]
    for fid in files:
        if not os.path.exists(glacier + "/" + fid):
            url = "http://students.washington.edu/shapero/mathieu_bedmaps"
            os.system("wget " + url + "/" 
                            + glacier + "/" + fid + " -P " + glacier)


    print('Done making DEMs for '+glacier)


############################################################################
## Do some extra junk for Jakobshavn                                      ##
############################################################################
(x, y, vx) = read_dem('jakobshavn/UDEM.xy')
(x, y, vy) = read_dem('jakobshavn/VDEM.xy')

ny, nx = np.shape(vx)
dx = x[1] - x[0]


# First, find all the external points where we don't have any data using a
# depth-first search, and re-label them as such
stack = [ (0, 0) ]
q = np.copy(vx)
q[0, 0] = -3.0e+9

while stack:
    (i, j) = stack.pop()
    q[i, j] = -4.0e+9

    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            k = (i + di) % ny
            l = (j + dj) % nx

            if q[k, l] == -2.0e+9:
                q[k, l] = -3.0e+9
                stack.append( (k, l) )

I, J = np.where(q == -2.0e+9)
nn = len(I)
print(nn)


# Then find all the internal points with missing data, and interpolate a
# value to them using inverse cube distance weighting
for m in range(nn):
    i = I[m]
    j = J[m]

    vx[i, j] = 0.0
    vy[i, j] = 0.0

    weights = 0.0

    for di in range(-4, 5):
        for dj in range(-4, 5):
            k = i + di
            l = j + dj

            if q[k, l] > -2.0e+9:
                weight = 1.0 / np.sqrt(di**2 + dj**2)**3
                vx[i, j] += weight * vx[k, l]
                vy[i, j] += weight * vy[k, l]
                weights += weight

            if weights != 0.0:
                vx[i, j] /= weights
                vy[i, j] /= weights
            else:
                print ("{0} {1}\n".format(i, j))


# Finally, write all the results out to a file
fidu = open('jakobshavn/UDEM0.xy', 'w')
fidv = open('jakobshavn/VDEM0.xy', 'w')


for fid in [fidu, fidv]:
    fid.write('{0}\n{1}\n'.format(nx,ny))

for j in range(nx):
    for i in range(ny):
        fidu.write('{0} {1} {2}\n'.format(x[j],y[i],vx[i,j]))
        fidv.write('{0} {1} {2}\n'.format(x[j],y[i],vy[i,j]))

for fid in [fidu, fidv]:
    fid.close()


print("Done post-processing Jakobshavn")

