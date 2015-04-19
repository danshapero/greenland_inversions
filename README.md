greenland_inversions
====================
Code and scripts I use for inverting glacier bed stress for Kangerd, Helheim, Jakobshavn glaciers

Dependencies:
* python
* python-scipy, python-numpy
* python-gdal
* python-netCDF4
* metis
* an MPI implementation
* libscalapack-mpi1, libscalapack-mpi-dev
* libmumps-4.10.0, libmumps-dev
* elmer

To fetch all the various data, run the command

```python initialize.py -d <dem source>  -f <SIA fraction> -l <triangle width> -p <mesh partitions>```

where `<dem source>` is either `morlighem` or `cresis` depending on whose DEM you wish to use, and `<SIA fraction>` is the fraction of the fraction of the driving stress that the bed is assumed to support at the margins. I usually used `0.5`. The triangle argument specifies the diameter of the smallest triangles in the mesh, i.e. in the fastest-flowing parts of the glacier; elsewhere, the mesh will be coarsened. This script will fetch some fairly big data sets (> 2GB total).

To build the helper functions used by Elmer, the `elmerf90` executable must be on your path and `libelmer.so` has to be on your library search path.

To run the code, execute

```python run.py -g <glacier>  -r <regularization>  -i <iterations> -o <output file>```

where `<glacier>` is the name of the glacier (either "helheim", "kangerd" or "jakobshavn"), `<regularization>` is the value of the Tikhonov regularization parameter, `<iterations>` is the number of iterations used in the optimization procedure and `<output file>` is the (optional) location of a file to store all of Elmer's diagnostic info. Only the `<glacier>` argument is required; the regularization parameter and iteration count default to 1.0e10 and 50 respectively if you do not provide them.

On the machines I use, an inversion with 4 cores takes 16 hours for a small mesh like Kangerd and 2 days for a bigger one like Jakobshavn at moderate resolution.
