#!/usr/bin/env python

import sys
import os

from data import make_data
from dems import make_dems, make_beta, make_temp
from meshes import make_meshes
from elmer import make_elmer_meshes


# ---------------------------------------------------------------------------- #
def main(argv):                                                                #
# ---------------------------------------------------------------------------- #
    os.system("make all")

    os.chdir("data")
    make_data.main(argv)
    os.chdir("../")

    os.chdir("dems")
    make_dems.main(argv)
    make_temp.main(argv)
    make_beta.main(argv)
    os.chdir("../")

    os.chdir("meshes")
    make_meshes.main(argv)
    os.chdir("../")

    os.chdir("elmer")
    make_elmer_meshes.main(argv)
    os.chdir("../")




# ---------------------------------------------------------------------------- #
if __name__ == "__main__":                                                     #
# ---------------------------------------------------------------------------- #
    main(sys.argv[1:])

