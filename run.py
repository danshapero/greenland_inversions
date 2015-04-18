
import sys
import argparse
import os
from elmer import sif_files

# ------------
def main(argv):
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--glacier", required = True,
                        help = "Name of glacier for inversion; either "
                               "'jakobshavn', 'helheim' or 'kangerd'.")
    parser.add_argument("-p", "--partitions", required = True,
                        help = "Number of mesh partitions.")
    parser.add_argument("-r", "--regularization", required = False,
                        help = "Value of the regularization parameter.")
    parser.add_argument("-i", "--iterations", required = False,
                        help = "Number of iterations for the optimization"
                               " procedure.")
    parser.add_argument("-o", "--output", required = False,
                        help = "Name of file to save Elmer logs to.")

    args, _ = parser.parse_known_args(argv)

    partitions = int(args.partitions)
    glacier = args.glacier

    regularization = 1.0e10
    if args.regularization:
        regularization = float(args.regularization)

    max_iterations = 35
    if args.iterations:
        max_iterations = int(args.iterations)

    # Generate a .sif file with the desired parameters
    sif_files.generate_sif_file(glacier,
                                regularization = regularization,
                                max_iterations = max_iterations)

    # Set an environment variable for the glacier we're currently simulating.
    # This is necessary to convey information to Fortran procedures where we
    # can't pass this information as a function argument due to restrictions
    # in Elmer.
    os.environ["glacier"] = glacier

    startinfo = open("ELMERSOLVER_STARTINFO", "w")
    startinfo.write("elmer/Robin_Beta_" + glacier.title() + ".sif")
    startinfo.close()

    # Run Elmer and optionally pipe the output to a text file
    output_cmd = ""
    if args.output:
        output_cmd = " > " + args.output + " 2>&1"
    os.system("nice -n7 mpirun -n " + str(partitions)
              + " ElmerSolver_mpi" + output_cmd)


# -----------------------
if __name__ == "__main__":
    main(sys.argv[1:])
