
import sys
import shutil
import tarfile
import tempfile
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


# ------------------------------------------------------------------
def l_curve_point(archive_name, glacier, regularization, partitions):
    # Extract the archive of simulation results to a temporary directory
    temp_dir_name = tempfile.mkdtemp()
    tar = tarfile.open(name = archive_name, mode = 'r:gz')
    tar.extractall(path = temp_dir_name)
    tar.close()

    # Get the inverted basal friction parameter and compute
    #    integral |grad beta|^2 dx
    x, y, ele, bnd = read_triangle_mesh(temp_dir_name + "/meshes/" +
                                        glacier + '/' + glacier + ".2")
    tri = Triangulation(x, y, ele)
    beta = get_field("beta", temp_dir_name + "/elmer/" + glacier + "3d",
                     partitions, tri, surface = "bottom")
    grad_beta_square = square_gradient(tri, beta)

    # Get the value of the total cost function from the Elmer log file
    log_file_name = "helheim_lambda-" + str(regularization) + ".txt"
    with open(temp_dir_name + '/' + log_file_name, "r") as log_file:
        cost_function = get_error_from_elmer_log(log_file.read())

    # Delete the temporary directory
    shutil.rmtree(temp_dir_name)

    return cost_function, grad_beta_square


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
