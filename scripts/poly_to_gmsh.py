
from meshes import read_poly
import numpy as np
import sys


# ---------------------------------------------
def poly_to_gmsh(poly_filename, gmsh_filename):
# ---------------------------------------------
    x, y, bnd, edge, xh, yh = read_poly(poly_filename)

    nn = len(x)
    ne = np.shape(edge)[0]

    edges = np.zeros((ne + 1, 2), dtype = np.int32)
    edges[1:,:] = map(lambda i: i + 1, edge)

    del edge

    # Find all the loops of the PSLG
    loops = []

    unvisited = set(range(1, nn + 1))
    while unvisited:
        i = unvisited.pop()
        loop = [i]
        j = edges[i, 1]
        while j != i:
            loop.append(j)
            unvisited.remove(j)
            j = edges[j, 1]

        loops.append(loop)

    del edges

    num_loops = len(loops)
    offset = np.zeros(num_loops + 1, dtype = np.int32)
    for l in range(num_loops):
        offset[l + 1] = offset[l] + len(loops[l])

    fid = open(gmsh_filename, "w")

    # Write out the positions of the nodes
    fid.write("cl = 1.0e+22;\n")
    fid.write("// Mesh points\n")
    for i in range(nn):
        fid.write("Point({0}) = {{{1}, {2}, 0.0, cl}};\n"
                  .format(i+1, x[i], y[i]))
    fid.write("\n")

    fid.write("// Mesh edges\n")
    for l in range(num_loops):
        loop = loops[l]
        nl = len(loop)
        for k in range(nl):
            fid.write("Line({0}) = {{{1}, {2}}};\n"
                      .format(offset[l] + k + 1, loop[k], loop[(k+1)%nl]))

    fid.write("\n")

    fid.write("// Line loops for the boundary\n")
    for l in range(num_loops):
        loop = loops[l]
        nl = len(loop)
        fid.write("Line Loop({0}) = {{{1}"
                  .format(offset[-1] + l + 1, loop[0]))
        for k in range(1, nl):
            fid.write(", {0}".format(loop[k]))
        fid.write("};\n")
    fid.write("\n")

    fid.write("Plane Surface ({0}) = {{{1}"
              .format(offset[-1] + num_loops + 1, offset[-1] + 1))
    for l in range(1, num_loops):
        fid.write(", {0}".format(offset[-1] + l + 1))
    fid.write("};\n\n")
    fid.write("Recombine Surface{{{0}}};\n"
              .format(offset[-1] + num_loops + 1))
    fid.write("\n")

    fid.write("Mesh.Algorithm = 8;\n")
    fid.write("Mesh.SubdivisionAlgorithm = 1;\n\n")


if __name__ == "__main__":
    poly_to_gmsh(sys.argv[1], sys.argv[2])
