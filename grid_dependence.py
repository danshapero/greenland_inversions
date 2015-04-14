#!/usr/bin/env python

import sys
import os
import glob
import shutil

from meshes import make_meshes
from elmer import make_elmer_meshes
import run

# ------------
def main(argv):
    """
    This script runs inversions for Helheim at successively higher
    mesh resolution.
    """

    glacier = "helheim"

    dxs = [300, 150, 75]
    for dx in dxs:
        os.chdir("meshes")
        make_meshes.main(["-l", str(dx)])
        os.chdir("../")

        os.chdir("elmer")
        make_elmer_meshes.main(argv)
        os.chdir("../")

        directory = glacier + "_grid_dependence"
        os.mkdir(directory)
        log_file_name = directory + "/log_dx-" + str(dx) + ".txt"

        run.main(["-g", glacier,
                  "-i", "20",
                  "-o", log_file_name])

        for filename in glob.glob("meshes/" + glacier + "/"
                                  + glacier + ".[1-2]*"):
            shutil.move(filename, directory)

        shutil.move("elmer/" + glacier + "3d", directory)
        shutil.rmtree("elmer/" + glacier)


# -----------------------
if __name__ == "__main__":
    main(sys.argv[1:])
