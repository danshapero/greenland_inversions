#!/usr/bin/env python

import sys
import argparse
import os
import numpy as np
from netCDF4 import Dataset

from scripts.geodat import *
from scripts.geotif import *
import postprocess_jak


# ---------------------------------------------------------------------------- #
def main(argv):                                                                #
# ---------------------------------------------------------------------------- #
    # Parse command line arguments
    dem_source = "morlighem"

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dem", required = True,
                        help = "DEM source, either 'cresis' or 'morlighem'")
    args, _ = parser.parse_known_args(argv)
    dem_source = args.dem

    if not dem_source in ("morlighem", "cresis"):
        print("Unrecognized DEM source " + dem_source + ", should be\n"
              "either \"cresis\" or \"morlighem\"\n")
        sys.exit(1)

    glaciers = ["helheim", "kangerd", "jakobshavn"]

    # -------------------------
    # Make velocity data files
    # -------------------------
    for glacier in glaciers:
        if not os.path.exists(glacier):
            os.makedirs(glacier)

        # Check to see if the velocity data have already been made
        if not( os.path.exists(glacier + '/UDEM.xy') or
                os.path.exists(glacier + '/VDEM.xy')):

            # Read in the raw velocity data files
            filename = '../data/' + glacier + "/mosaicOffsets"
            x, y, vx = read_geodat(filename + ".vx")
            _, _, vy = read_geodat(filename + ".vy")

            nx = len(x)
            ny = len(y)

            # Find the points where there actually is measured velocity data
            I, J = np.where(vx != -2.0e+9)
            imin, imax = max(0, min(I) - 2), min(nx - 2, max(I) + 2)
            jmin, jmax = max(0, min(J) - 2), min(nx - 2, max(J) + 2)
            del I, J
            
            vx = vx[imin: imax+1, jmin: jmax+1]
            vy = vy[imin: imax+1, jmin: jmax+1]

            x = x[jmin: jmax+1]
            y = y[imin: imax+1]
            nx = jmax - jmin + 1
            ny = imax - imin + 1

            # Write out the velocity data
            fidu = open(glacier + '/UDEM.xy', 'w')
            fidv = open(glacier + '/VDEM.xy', 'w')

            for fid in [fidu, fidv]:
                fid.write('{0}\n{1}\n'.format(nx, ny))
                
            for j in range(nx):
                for i in range(ny):
                    fidu.write('{0} {1} {2}\n'.format(x[j], y[i], vx[i,j]))
                    fidv.write('{0} {1} {2}\n'.format(x[j], y[i], vy[i,j]))

            for fid in [fidu, fidv]:
                fid.close()

            # Delete the velocities
            del vx, vy

        print("Done making velocity data for " + glacier)


    # ----------------------------------
    # Make surface / bed elevation data
    # ----------------------------------

    if dem_source == "morlighem":
        morlighem_data = Dataset("../data/MCdataset-2014-11-19.nc", "r")
        x = morlighem_data.variables['x'][:]
        y = morlighem_data.variables['y'][:]

        xmin, xmax = np.min(x), np.max(x)
        ymin, ymax = np.min(y), np.max(y)

        dx = np.abs(x[1] - x[0])
        dy = np.abs(y[1] - y[0])

        rects = {"helheim": ((249775.0, 310825.0),
                             (-2592825.0, -2513625.0)),
                 "kangerd": ((448375.0, 495025.0),
                             (-2300325.0, -2251725.0)),
                 "jakobshavn": ((-209985.0, -135015.0),
                                (-2314985.0, -2245025.0))}

        for glacier, r in rects.iteritems():
            jmin = int( (r[0][0] - xmin) / dx )
            jmax = int( (r[0][1] - xmin) / dx )
            imin = int( (r[1][0] - ymin) / dy )
            imax = int( (r[1][1] - ymin) / dy )

            nxp = jmax - jmin
            nyp = imax - imin

            xp = x[jmin:jmax]
            yp = y[imin:imax]

            B = np.zeros((nyp, nxp), dtype = np.float64)
            S = np.zeros((nyp, nxp), dtype = np.float64)
            B[:,:] = morlighem_data.variables["bed"][imin:imax, jmin:jmax]
            S[:,:] = morlighem_data.variables["surface"][imin:imax, jmin:jmax]

            yp = yp[::-1]
            B = B[::-1, :]
            S = S[::-1, :]

            fields = {"zbDEM.xy": B, "zsDEM.xy": S}
            for filename, field in fields.iteritems():
                file = open(glacier + '/' + filename, 'w')
                file.write("{0}\n{1}\n".format(nxp, nyp))
                for j in range(nxp):
                    for i in range(nyp):
                        if field[i, j] == -9999.0:
                            field[i, j] = -2.0e+9
                        file.write("{0} {1} {2}\n"
                                   .format(xp[j], yp[i], field[i, j]))

        morlighem_data.close()

    #else:
        # TODO: unzip the files from CReSIS and convert their contents from
        # the QGIS format to the one Elmer expects


    if not os.path.exists("jakobshavn/zsDEM.xy"):
        # Make DEMs for Jakobshavn from special data
        if dem_source == "morlighem":
            # read the raw data
            x, y, s = read_geodat("../data/jakobshavn/dem13Mar.smooth")
            nx = len(x)
            ny = len(y)

            # write out the surface data in the format Elmer expects
            fid = open("jakobshavn/zsDEM.xy", "w")
            fid.write("{0}\n{1}\n".format(nx, ny))
            for j in range(nx):
                for i in range(ny):
                    fid.write('{0} {1} {2}\n'.format(x[j], y[i], s[i, j]))
            fid.close()
        else:
            os.system("wget " + surface_dem_url
                        + "jakobshavn/zsDEM.xy -P jakobshavn")
       

    print ("Done making surface elevation for Jakobshavn")

    # Post-process the Jakobshavn velocities to interpolate over some small
    # gaps in the observational data
    postprocess_jak.main()

    print("Done post-processing Jakobshavn velocity data")


if __name__ == "__main__":
    main(sys.argv[1:])

