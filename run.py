
import sys
import argparse
import os
from sif_template import generate_sif_file

# ------------
def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--glacier", required = True,
                        help = "Name of glacier for inversion; either "
                               "'jakobshavn', 'helheim' or 'kangerd'.")
    parser.add_argument("-r", "--regularization", required = False,
                        help = "Value of the regularization parameter.")
    parser.add_argument("-i", "--iterations", required = False,
                        help = "Number of iterations for the optimization"
                               " procedure.")
    parser.add_argument("-o", "--output", required = False,
                        help = "Name of file to save Elmer logs to.")

    args, _ = parser.parse_known_args(argv)

    glacier = args.glacier

    regularization = 1.0e10
    if args.regularization:
        regularization = float(args.regularization)

    max_iterations = 35
    if args.iterations:
        max_iterations = int(args.iterations)

    generate_sif_file(glacier,
                      regularization = regularization,
                      max_iterations = max_iterations)

    os.environ["glacier"] = glacier

    startinfo = open("ELMERSOLVER_STARTINFO", "w")
    startinfo.write("elmer/Robin_Beta_" + glacier.title() + ".sif")
    startinfo.close()

    output_cmd = ""
    if args.output:
        output_cmd = " > " + args.output + " 2>&1"
    os.system("nice -n7 mpirun -n 4 ElmerSolver_mpi" + output_cmd)


# -----------------------
if __name__ == "__main__":
    main(sys.argv[1:])
