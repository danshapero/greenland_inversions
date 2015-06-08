#!/usr/bin/env python

import sys
import os
import shutil
import tarfile
import tempfile
import argparse
from os.path import expanduser

from matplotlib.tri import *        # Note: need matplotlib 1.4.2

from scripts.elmer import *
from scripts.meshes import *
from scripts.write_qgis import *



# ----------------------------------------------------------
def pp_directory(mesh_file, elmer_dir, partitions, out_file):
    """
    Post-process the output from an Elmer inversion into several Arc/Info Grid
    files that can be read by e.g. ArcGIS, QGIS, etc.

    Parameters:
    ==========
    mesh_file:  the stem of the Triangle mesh used in the Elmer inversions, e.g
                if the Triangle mesh was "dir/meshes/helheim.3.<node|ele|..>"
                then the stem would be "dir/meshes/helheim.3".
    elmer_dir:  the directory containing the Elmer output files,
                "Test_Robin_Beta.result.<partition>"
    partitions: number of parallel partitions used for the inversion
    out_file:   desired stem of the output files

    Writes:
    ======
    <out_file>_taub.txt: computed basal shear stress
    <out_file>_uh.txt:   computed depth-averaged velocities
    <out_file>_ub.txt:   computed basal velocities
    <out_file>_us.txt:   computed surface velocities
    <out_file>_uso.txt:  input surface velocities
    """
    # Load in the Triangle mesh for the glacier
    xm, ym, ele, bnd = read_triangle_mesh(expanduser(mesh_file))
    tri = Triangulation(xm, ym, ele)

    # Get the basal friction parameter from Elmer
    beta = get_field("beta", elmer_dir, partitions, tri, surface = "bottom")

    # Get the computed basal velocities
    uxb = get_field("velocity 1", elmer_dir, partitions, tri, surface = "bottom")
    uyb = get_field("velocity 2", elmer_dir, partitions, tri, surface = "bottom")

    # Get the computed surface velocities
    uxs = get_field("velocity 1", elmer_dir, partitions, tri, surface = "top")
    uys = get_field("velocity 2", elmer_dir, partitions, tri, surface = "top")

    # Get the observed surface velocities
    uxso = get_field("velod 1", elmer_dir, partitions, tri, surface = "top")
    uyso = get_field("velod 2", elmer_dir, partitions, tri, surface = "top")

    # Get the computed depth-averaged velocities
    uxh = get_field("velod 1", elmer_dir, partitions, tri, surface = "average")
    uyh = get_field("velod 2", elmer_dir, partitions, tri, surface = "average")

    # Interpolate the results to a regularly spaced grid
    xmin = 100.0 * math.floor(np.min(xm)/100.0)
    xmax = 100.0 * math.ceil(np.max(xm)/100.0)
    ymin = 100.0 * math.floor(np.min(ym)/100.0)
    ymax = 100.0 * math.ceil(np.max(ym)/100.0)

    x = np.linspace(xmin, xmax, (xmax - xmin)/100.0 + 1)
    y = np.linspace(ymin, ymax, (ymax - ymin)/100.0 + 1)

    nx = len(x)
    ny = len(y)

    tau = -9999.0 * np.ones((ny, nx))
    us  = -9999.0 * np.ones((ny, nx))
    ub  = -9999.0 * np.ones((ny, nx))
    uh  = -9999.0 * np.ones((ny, nx))
    uso = -9999.0 * np.ones((ny, nx))

    # Note: this part needs matplotlib 1.4.2 to work correctly
    finder = tri.get_trifinder()
    interp_beta = LinearTriInterpolator(tri, beta, trifinder = finder)
    interp_uxb = LinearTriInterpolator(tri, uxb,   trifinder = finder)
    interp_uyb = LinearTriInterpolator(tri, uyb,   trifinder = finder)
    interp_uxs = LinearTriInterpolator(tri, uxs,   trifinder = finder)
    interp_uys = LinearTriInterpolator(tri, uys,   trifinder = finder)
    interp_uxh = LinearTriInterpolator(tri, uxh,   trifinder = finder)
    interp_uyh = LinearTriInterpolator(tri, uyh,   trifinder = finder)
    interp_uxso = LinearTriInterpolator(tri, uxso, trifinder = finder)
    interp_uyso = LinearTriInterpolator(tri, uyso, trifinder = finder)

    for i in range(ny):
        for j in range(nx):
            k = int(finder(x[j], y[i]))
            if k != -1:
                Beta = interp_beta(x[j], y[i])
                Uxb  = interp_uxb(x[j], y[i])
                Uyb  = interp_uyb(x[j], y[i])
                Uxs  = interp_uxs(x[j], y[i])
                Uys  = interp_uys(x[j], y[i])
                Uxh  = interp_uxh(x[j], y[i])
                Uyh  = interp_uyh(x[j], y[i])
                Uxso = interp_uxso(x[j], y[i])
                Uyso = interp_uyso(x[j], y[i])

                ub[i, j] = math.sqrt(Uxb**2 + Uyb**2)
                us[i, j] = math.sqrt(Uxs**2 + Uys**2)
                uh[i, j] = math.sqrt(Uxh**2 + Uyh**2)
                uso[i, j] = math.sqrt(Uxso**2 + Uyso**2)
                tau[i, j] = 1000 * Beta**2 * ub[i, j]

    # Write the interpolated basal shear stress to the QGIS format
    write_to_qgis(out_file + "_taub.txt", tau, x[0], y[0], 100.0, -9999)
    write_to_qgis(out_file + "_us.txt",   us,  x[0], y[0], 100.0, -9999)
    write_to_qgis(out_file + "_ub.txt",   ub,  x[0], y[0], 100.0, -9999)
    write_to_qgis(out_file + "_uso.txt",  uso, x[0], y[0], 100.0, -9999)
    write_to_qgis(out_file + "_uh.txt",   uh,  x[0], y[0], 100.0, -9999)



# ---------------------------------------------------------
def pp_archive(archive_name, glacier, partitions, out_file):
    """
    Same thing as pp_directory, only on a .tar archive containing the Elmer
    results as output by the `archive.py` script.
    """
    # Extract the archive of simulation results to a temporary directory
    temp_dir_name = tempfile.mkdtemp()
    tar = tarfile.open(name = archive_name, mode = 'r:gz')
    tar.extractall(path = temp_dir_name)
    tar.close()

    pp_directory(temp_dir_name + "/meshes/" + glacier + '/' + glacier + ".2",
                 temp_dir_name + "/elmer/"  + glacier + "3d",
                 partitions,
                 temp_dir_name + '/' + glacier)

    tar = tarfile.open(name = out_file, mode = 'w:gz')
    tar.add(temp_dir_name)
    tar.close()

    shutil.rmtree(temp_dir_name)



# ------------
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--elmer", required = True,
                        help = "Directory or archive of Elmer result files")
    parser.add_argument("-o", "--output", required = True,
                        help = "Location for output")
    parser.add_argument("-p", "--partitions", required = True,
                        help = "Number of mesh partitions")
    parser.add_argument("-m", "--mesh", required = False,
                        help = "Path to triangle mesh and file stem; required"
                        " if post-processing from directory.")
    parser.add_argument("-g", "--glacier", required = False,
                        help = "Name of glacier; required if post-processing"
                        " from .tar archive.")

    args, _ = parser.parse_known_args(argv)

    elmer = args.elmer
    out_file = args.output
    partitions = int(args.partitions)

    if os.path.isdir(elmer):
        mesh_file = args.mesh
        pp_directory(mesh_file, elmer, partitions, out_file)
    else:
        glacier = args.glacier
        pp_archive(elmer, glacier, partitions, out_file)


if __name__ == "__main__":
    main(sys.argv[1:])
