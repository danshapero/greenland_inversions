
from scripts.elmer import get_error_from_elmer_log
import run
import archive

import sys
import numpy as np


# ------------
def main(argv):
    """
    This script runs several inversions for Helheim glacier using
    different values of the regularization parameter in order to
    generate the familiar L-curve plot.
    """

    rmin = float(argv[0])
    rmax = float(argv[1])
    nr   = int(argv[2])

    rs = np.logspace(rmin, rmax, nr)

    for n in range(nr):
        r = rs[n]
        log_file_name = "helheim_lambda-" + str(r) + ".txt"

        run.main(["-g", "helheim",
                  "-r", str(r),
                  "-i", "30",
                  "-o", log_file_name])

        archive.main(["-g", "helheim",
                      "-o", "helheim_lambda-" + str(r) + ".tar.gz",
                      "-x", log_file_name])

if __name__ == "__main__":
    main(sys.argv[1:])
