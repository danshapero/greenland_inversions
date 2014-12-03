#!/usr/bin/env python

import os

glaciers = ["helheim", "kangerd", "jakobshavn"]


# ---------------------------------------------------------------------------- #
def main(argv):                                                                #
# ---------------------------------------------------------------------------- #
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

        # Extrude the mesh
        if not os.path.exists(glacier + "3d/mesh.header"):
            os.system("../ExtrudeMesh " + glacier + ' ' + glacier + 
                "3d 11 1 1 0 0 0 0 ../dems/" + glacier + " 250.0 3 -2.0e9")

        if not os.path.exists(glacier + "3d/partitioning.4/part.1.header"):
            os.system("ElmerGrid 2 2 " + glacier + "3d -metis 4 -removeunused")


# ---------------------------------------------------------------------------- #
if __name__ == "__main__":                                                     #
# ---------------------------------------------------------------------------- #
    main(sys.argv[1:])

