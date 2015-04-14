
from scripts.elmer import get_error_from_elmer_log
import run

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
    err = np.zeros(nr)

    for n in range(nr):
        r = rs[n]
        log_file_name = "helheim_lambda-" + str(r) + ".txt"

        run.main(["-g", "helheim",
                  "-r", str(r),
                  "-i", "20",
                  "-o", log_file_name])

        with open(log_file_name, "r") as log_file:
            err[n] = get_error_from_elmer_log(log_file.read())

    with open("L_curve_data.txt", "w") as output_file:
        output_file.write("{0} {1}\n".format(rs[n], err[n]))


if __name__ == "__main__":
    main(sys.argv[1:])
