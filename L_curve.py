
import sys
import numpy as np

from matplotlib.tri import *

from scripts.elmer import get_error_from_elmer_log, get_field
from scripts.meshes import read_triangle_mesh, area
import run
import archive


# -------------------------
def square_gradient(tri, q):
    """
    Given a triangulation object and a field `q` defined at the vertices of
    the triangulation, return
        integral |grad q|^2 dx
    """

    finder = tri.get_trifinder()
    interp = LinearTriInterpolator(tri, q, trifinder = finder)

    integral = 0.0
    num_triangles, _ = np.shape(tri.triangles)

    for n in range(num_triangles):
        ele = tri.triangles[n, :]
        x = tri.x[ele]
        y = tri.y[ele]

        a = area(x, y)
        q_x, q_y = interp.gradient(sum(x) / 3, sum(y) / 3)

        integral += a * (q_x.data**2 + q_y.data**2)

    return integral


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
                  "-p", "4",
                  "-i", "30",
                  "-o", log_file_name])

        archive.main(["-g", "helheim",
                      "-o", "helheim_lambda-" + str(r) + ".tar.gz",
                      "-x", log_file_name])

if __name__ == "__main__":
    main(sys.argv[1:])
