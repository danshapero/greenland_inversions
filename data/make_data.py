#!/usr/bin/env python

import sys
import argparse
import os

# ---------------------------------------------------------------------------- #
def main(argv):                                                                #
# ---------------------------------------------------------------------------- #
    dem_source = "morlighem"

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dem", required = True,
                        help = "DEM source, either 'cresis' or 'morlighem'")
    args, _ = parser.parse_known_args(argv)
    dem_source = args.dem

    if not dem_source in ("morlighem", "cresis"):
        print("Unrecognized DEM source " + dem_source + ", should be\n"
              "either \"cresis\" or \"morlighem\"\n")
        sys.exit(1)


    # ------------------------
    # Retrieve elevation data
    # ------------------------
    if dem_source == "morlighem":
        os.system("wget ftp://sidads.colorado.edu/DATASETS/"
                  "IDBMG4_BedMachineGr/MCdataset-2014-11-19.nc")
    else:
        os.system("wget ftp://data.cresis.ku.edu/data/temp/"
                  "for_OIBlandice/Helheim_2006_2013_Composite.zip "
                  "-P helheim")
        os.system("wget ftp://data.cresis.ku.edu/data/temp/"
                  "for_OIBlandice/Kangerdlugssuaq_2006_2013_Composite.zip "
                  "-P kangerd")
        os.system("wget ftp://data.cresis.ku.edu/data/grids/old_versions/"
                  "Jakobshavn_2006_2012_Composite.zip "
                  "-P jakobshavn")


    # -----------------------
    # Retrieve velocity data
    # -----------------------

    # Dictionary to store names of glacier velocity data files and URLs for
    # where to find them on the internet
    helheim_files = {
        'TSX_E66.50N_27Jan09_07Feb09': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-66.50N/TSX_Jan-27-2009_Feb-07-2009_19-57-11/'}

    jakobshavn_files = {
        'mosaicOffsets': 'http://students.washington.edu/shapero/jakobshavn/'
    }

    kangerd_files = {
        'TSX_E68.80N_28Jan09_08Feb09': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-68.80N/TSX_Jan-28-2009_Feb-08-2009_19-40-29/'}

    glacier_data = {
        'helheim': helheim_files,
        'jakobshavn': jakobshavn_files,
        'kangerd': kangerd_files
    }

    # Make directories
    for glacier in glacier_data.keys():
        if not os.path.exists(glacier):
            os.makedirs(glacier)

    # Retrieve velocity data
    extensions = ['.vx', '.vx.geodat', '.vy', '.vy.geodat',
                    '.ex', '.ex.geodat', '.ey', '.ey.geodat', '.meta']
    for glacier in glacier_data.keys():
        for filestem in glacier_data[glacier].keys():
            for e in extensions:
                filename = filestem + e
                if not os.path.exists(glacier + '/' + filename):
                    url = glacier_data[glacier][filestem] + filename
                    os.system('wget ' + url + ' -P ' + glacier)


    # -------------------------------------
    # Retrieve temperature / rheology data
    # -------------------------------------
    url = "http://students.washington.edu/shapero/"
    for glacier in ["helheim", "kangerd", "jakobshavn"]:
        filename = "xyzTA" + glacier + ".txt"
        if not os.path.exists(glacier + '/' + filename):
            os.system("wget " + url + "temp_data/"
                        + filename + ' -P ' + glacier)


    # -------------------------------------------------------
    # Retrieve special surface elevation data for Jakobshavn
    # -------------------------------------------------------
    url = "http://students.washington.edu/shapero/jakobshavn/"
    if not os.path.exists("jakobshavn/dem13Mar.smooth"):
        os.system("wget " + url + "dem13Mar.smooth -P jakobshavn")
        os.system("wget " + url + "dem13Mar.smooth.geodat -P jakobshavn")



# ---------------------------------------------------------------------------- #
if __name__ == "__main__":                                                     #
# ---------------------------------------------------------------------------- #
    main(sys.argv[1:])

