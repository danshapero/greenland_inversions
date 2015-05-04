
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
    parser.add_argument("-x", "--extra", required = False, nargs = '*',
                        help = "Extra files to pack into the archive,"
                               " e.g. log files.")

    args, _ = parser.parse_known_args(argv)

    glacier = args.glacier
    output  = args.output
    extras  = args.extra

    tar = tarfile.open(name = output, mode = 'w:gz')

    for dir in ["data", "dems", "elmer", "meshes"]:
        tar.add(dir + "/" + glacier)

    tar.add("elmer/" + glacier + "3d")

    for filename in extras:
        tar.add(filename)

    tar.close()


if __name__ == "__main__":
    main(sys.argv[1:])
