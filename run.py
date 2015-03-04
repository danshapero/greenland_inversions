
import sys
import os


# ------------
def main(argv):
    glacier = argv[0]
    os.environ["glacier"] = glacier

    startinfo = open("ELMERSOLVER_STARTINFO", "w")
    startinfo.write("elmer/Robin_Beta_" + glacier.title() + ".sif")
    startinfo.close()

    os.system("nice -n7 mpirun -n 4 ElmerSolver_mpi")


# -----------------------
if __name__ == "__main__":
    main(sys.argv[1:])
