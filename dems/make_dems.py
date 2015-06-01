#!/usr/bin/env python

import sys
import argparse
import os
import numpy as np
from netCDF4 import Dataset

from scripts.geodat import *
from scripts.geotif import *
from fixup import fixup_data


# ------------
def main(argv):
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

            fixup_data(glacier + "/UDEM.xy", 12)
            fixup_data(glacier + "/VDEM.xy", 12)

        print("Done making velocity data for " + glacier)


    # ----------------------------------
    # Make surface / bed elevation data
    # ----------------------------------

    rects = {"helheim": ((249775.0, 310825.0),
                         (-2592825.0, -2513625.0)),
             "kangerd": ((448375.0, 495025.0),
                         (-2300325.0, -2251725.0)),
             "jakobshavn": ((-209985.0, -135015.0),
                            (-2314985.0, -2245025.0))}

    for glacier in glaciers:
        # If we're using the mass-conserving bed DEM, extract the right window
        # for each glacier from the big netCDF file for all of Greenland
        if dem_source == "morlighem":
            morlighem_data = Dataset("../data/MCdataset-2014-11-19.nc", "r")
            x = morlighem_data.variables['x'][:]
            y = morlighem_data.variables['y'][:]

            xmin, xmax = np.min(x), np.max(x)
            ymin, ymax = np.min(y), np.max(y)

            dx = x[1] - x[0]
            dy = y[1] - y[0]

            r = rects[glacier]

            jmin = int( (r[0][0] - x[0]) / dx )
            jmax = int( (r[0][1] - x[0]) / dx )

            # Note that this is all weird because Morlighem's dataset goes
            # from north to south as indices increase
            imin = int( (r[1][1] - y[0]) / dy )
            imax = int( (r[1][0] - y[0]) / dy )

            nx = jmax - jmin
            ny = imax - imin

            x = x[jmin:jmax]
            y = y[imin:imax]

            B = np.zeros((ny, nx), dtype = np.float64)
            S = np.zeros((ny, nx), dtype = np.float64)
            B[:,:] = morlighem_data.variables["bed"][imin:imax, jmin:jmax]
            S[:,:] = morlighem_data.variables["surface"][imin:imax, jmin:jmax]

            y = y[::-1]
            B = B[::-1, :]
            S = S[::-1, :]

            morlighem_data.close()

        elif dem_source == "cresis":
            filename = "../data/" + glacier + "/" + glacier
            cresis_bed_data = open(filename + "_composite_bottom.txt", "r")
            cresis_surf_data = open(filename + "_composite_surface.txt", "r")

            nx = int(cresis_bed_data.readline().split()[1])
            ny = int(cresis_bed_data.readline().split()[1])
            xll = float(cresis_bed_data.readline().split()[1])
            yll = float(cresis_bed_data.readline().split()[1])
            dx = float(cresis_bed_data.readline().split()[1])
            dy = dx
            missing = float(cresis_bed_data.readline().split()[1])

            for k in range(6):
                cresis_surf_data.readline()

            x = [xll + k * dx for k in range(nx)]
            y = [yll + k * dy for k in range(ny)]

            B = np.zeros((ny, nx), dtype = np.float64)
            S = np.zeros((ny, nx), dtype = np.float64)

            for k in range(ny):
                B[k,:] = map(float, cresis_bed_data.readline().split())
                S[k,:] = map(float, cresis_surf_data.readline().split())

            cresis_bed_data.close()
            cresis_surf_data.close()

        # Write out the surface/bed DEMs
        fields = {"zbDEM.xy": B, "zsDEM.xy": S}
        for filename, field in fields.iteritems():
            file = open(glacier + '/' + filename, 'w')
            file.write("{0}\n{1}\n".format(nx, ny))
            for j in range(nx):
                for i in range(ny):
                    if field[i, j] == -9999.0:
                        field[i, j] = -2.0e+9
                    file.write("{0} {1} {2}\n"
                               .format(x[j], y[i], field[i, j]))


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



if __name__ == "__main__":
    main(sys.argv[1:])
