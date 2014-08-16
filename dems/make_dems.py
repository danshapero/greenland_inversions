#!/usr/bin/env python

import sys
sys.path.insert(0,'../scripts')

import os
from geodat import *
from geotif import *

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
                     'velocity': 'TSX_W69.10N_29Jan09_09Feb09',
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
        (imin,imax) = (min(I)-1,max(I)+1)
        (jmin,jmax) = (min(J)-1,max(J)+1)
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
    else:
        x = np.zeros(2)
        y = np.zeros(2)

        fid = open(glacier+'/UDEM.xy')
        nx = int(fid.readline().split()[0])
        ny = int(fid.readline().split()[0])

        (x[0],y[0]) = map(float,fid.readline().split()[0:2])
        h = float(fid.readline().split()[1])-y[0]
        x[1] = x[0]+nx*h
        y[1] = y[0]+ny*h



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

