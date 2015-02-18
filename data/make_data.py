#!/usr/bin/env python

import sys
import argparse
import os
import fnmatch

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
        if not os.path.exists("MCdataset-2014-11-19.nc"):
            os.system("wget ftp://sidads.colorado.edu/DATASETS/"
                      "IDBMG4_BedMachineGr/MCdataset-2014-11-19.nc")
    else:
        cresis_data = {
            "helheim": {"url": "temp/for_OIBlandice",
                        "dir": "Helheim_2006_2013_Composite"},
            "kangerd": {"url": "temp/for_OIBlandice",
                        "dir": "Kangerdlugssuaq_2006_2013_Composite"},
            "jakobshavn": {"url": "grids/old_versions",
                           "dir": "Jakobshavn_2006_2012_Composite"}
        }

        for glacier in cresis_data.keys():
            url = cresis_data[glacier]["url"]
            dir = cresis_data[glacier]["dir"]
            if not os.path.exists(glacier + "/" + dir):
                if not os.path.exists(glacier + "/" + dir + ".zip"):
                    os.system("wget ftp://data.cresis.ku.edu/data/"
                              + url + "/" + dir + ".zip -P " + glacier)
                os.system("unzip " + glacier + "/" + dir + ".zip"
                          + " -d " + glacier)
            for term in ["_composite_bottom.txt",
                         "_composite_surface.txt"]:
                if not os.path.exists(glacier + "/" + glacier + term):
                    for file in os.listdir(glacier + "/" + dir + "/grids"):
                        if fnmatch.fnmatch(file, "*" + term):
                            sfilename = glacier + "/" + dir + "/grids/" + file
                            dfilename = glacier + "/" + glacier + term
                            os.system("cp " + sfilename + " " + dfilename)


    # -----------------------
    # Retrieve velocity data
    # -----------------------
    glaciers = ["helheim", "kangerd", "jakobshavn"]

    # Make directories
    for glacier in glaciers:
        if not os.path.exists(glacier):
            os.makedirs(glacier)

    # Retrieve velocity data
    extensions = ['.vx', '.vx.geodat', '.vy', '.vy.geodat',
                    '.ex', '.ex.geodat', '.ey', '.ey.geodat', '.meta']
    website = "http://students.washington.edu/shapero/"
    for glacier in glaciers:
        for e in extensions:
            filename = "mosaicOffsets" + e
            if not os.path.exists(glacier + '/' + filename):
                url = website + glacier + '/' + filename
                os.system("wget " + url + ' -P ' + glacier)


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
