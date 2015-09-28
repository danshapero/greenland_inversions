
import sys
import os
import shutil
import tarfile
import tempfile

import math
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.tri import *

# Get matplotlib to use LaTeX
from matplotlib import rc
rc('font', **{'family':'sans-serif', 'sans-serif':['Arial']})
rc('text', usetex=True)

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
    log_file_name = "helheim_lambda-" + repr(regularization) + ".txt"
    with open(temp_dir_name + '/' + log_file_name, "r") as log_file:
        cost_function = get_error_from_elmer_log(log_file.read())

    # Delete the temporary directory
    shutil.rmtree(temp_dir_name)

    return cost_function, grad_beta_square


# ---------------
def analyze(argv):
    """
    This script analyzes the results of the main function and produces
    the L-curve plot.
    """
    costs = []
    tikhs = []
    regs  = []

    glacier = "helheim"
    extension = ".tar.gz"

    directory = argv[0]
    cached_output = os.path.join(directory, "helheim_l_curve.txt")
    if not os.path.exists(cached_output):
        for archive_name in [f for f in os.listdir(directory)
                             if (os.path.isfile(os.path.join(directory, f))
                                 and
                                 f[-len(extension):] == extension)]:
            start_index = len(glacier) + len("_lambda-")
            regularization = float(archive_name[start_index: -len(extension)])
            cost, tikh = l_curve_point(os.path.join(directory, archive_name),
                                       glacier, regularization, 4)
            costs.append(cost)
            tikhs.append(tikh)
            regs.append(regularization)

        with open(cached_output, 'w') as fid:
            fid.write("cost,model_norm,lambda\n")
            for k in range(len(costs)):
                fid.write("{0},{1},{2}\n".format(costs[k], tikhs[k], regs[k]))

    with open(cached_output, 'r') as fid:
        line = fid.readline()
        line = fid.readline().split('\n')[0]
        while(line):
            c, t, r = line.split(',')
            costs.append(float(c))
            tikhs.append(float(t))
            regs.append(float(r))
            line = fid.readline().split('\n')[0]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.scatter(tikhs, costs)
    for k in range(len(regs)):
        exponent = math.log(regs[k], 10)
        ax.annotate(r'$10^{{{0:.2f}}}$'.format(exponent),
                    xy = (tikhs[k], costs[k]),
                    xytext = (0, 30),
                    textcoords = 'offset points',
                    rotation = 45,
                    fontsize = 16)
    plt.xlabel(r'Model norm (MPa $\cdot$ m / a)', fontsize = 16)
    plt.ylabel(r'Cost function (MPa $\cdot$ m${}^3$ / a)', fontsize = 16)
    plt.xlim(0, 1.15 * np.max(tikhs))
    plt.ylim(0.95 * np.min(costs), 1.05 * np.max(costs))
    plt.show()

    return regs, tikhs, costs


# -----------
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
    if sys.argv[1] == "run":
        main(sys.argv[2:])
    else:
        analyze(sys.argv[2:])
