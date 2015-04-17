#!/usr/bin/env python

import sys
import argparse
import os

glaciers = ["helheim", "kangerd", "jakobshavn"]


# ------------
def main(argv):
    # Parse command line arguments
    dem_source = "morlighem"
    partitions = 4

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dem", required = True,
                        help = "DEM source, either 'cresis' or 'morlighem'")
    parser.add_argument("-p", "--partitions", required = True,
                        help = "Number of mesh partitions")
    args, _ = parser.parse_known_args(argv)
    dem_source = args.dem
    partitions = int(args.partitions)

    if not dem_source in ("morlighem", "cresis"):
        print("Unrecognized DEM source " + dem_source + ", should be\n"
              "either \"cresis\" or \"morlighem\"\n")
        sys.exit(1)

    for glacier in glaciers:
        # Make the directories for each glacier
        if not os.path.exists(glacier):
            os.makedirs(glacier)

        # Convert the triangle meshes to Elmer's format
        if not os.path.exists(glacier + "/mesh.header"):
            os.system("ElmerGrid 11 2 ../meshes/" + glacier + '/'
                        + glacier + ".2 -out " + glacier)

        # Make the bed.xyz and surf.xyz files because ExtrudeMesh is
        # hard-coded to use them.
        if (not os.path.exists("../dems/" + glacier + "/bed.xyz") or
            not os.path.exists("../dems/" + glacier + "/surf.xyz")):
            os.system("sed '1,2d' ../dems/" + glacier
                        + "/zbDEM.xy > ../dems/" + glacier + "/bed.xyz")
            os.system("sed '1,2d' ../dems/" + glacier
                        + "/zsDEM.xy > ../dems/" + glacier + "/surf.xyz")

        # Make directories for each glacier's 3d mesh
        if not os.path.exists(glacier + '3d'):
            os.makedirs(glacier + '3d')

        # Extrude the mesh. Need a different interpolation radius depending
        # on whose DEM we're using.
        dx = 250.0
        if dem_source == "cresis":
            dx = 750.0

        if not os.path.exists(glacier + "3d/mesh.header"):
            os.system("../ExtrudeMesh " + glacier + " " + glacier
                      + "3d 11 1 1 0 0 0 0 ../dems/" + glacier + " "
                      + str(dx) + " 3 -2.0e9")

        if not os.path.exists(glacier + "3d/partitioning.1/part.1.header"):
            os.system("ElmerGrid 2 2 " + glacier
                      + "3d -metis " + str(partitions) + " -removeunused")


# -----------------------
if __name__ == "__main__":
    main(sys.argv[1:])
