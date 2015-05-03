
import os
import sys
import argparse
import tarfile
import time

# ------------
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--glacier", required = True,
                        help = "Name of glacier for inversion.")
    parser.add_argument("-o", "--output", required = True,
                        help = "Name of output file.")

    args, _ = parser.parse_known_args(argv)

    glacier = args.glacier
    output  = args.output

    tar = tarfile.open(name = output, mode = 'w:gz')

    for dir in ["data", "dems", "elmer", "meshes"]:
        tar.add(dir + "/" + glacier)

    tar.add("elmer/" + glacier + "3d")

    tar.close()


if __name__ == "__main__":
    main(sys.argv[1:])
