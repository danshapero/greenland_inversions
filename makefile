.PHONY: data meshes clean



############################################################################
## Rules for fetching and processing data                                 ##
############################################################################
data:
	cd data && ./make_data.py && cd ../
	cd dems && ./make_dems.py && cd ../



############################################################################
## Rules for making meshes                                                ##
############################################################################
meshes: ExtrudeMesh data
	cd meshes && ./make_meshes.py && cd ../
	cd elmer && ./make_elmer_meshes.py && cd ../

ExtrudeMesh: ExtrudeMesh.c
	gcc ExtrudeMesh.c -o ExtrudeMesh -lm



############################################################################
## Rules for building libraries used for external functions in Elmer      ##
############################################################################
_SOURCES=USF_Init.f90 UWA_Bnd.f90 MU_Init.f90 Interp.f90
SOURCES = $(patsubst %,source/%,$(_SOURCES))

_SOLVERS=$(_SOURCES:.f90=.so)
SOLVERS=$(patsubst %,lib/%,$(_SOLVERS)) 

lib/%.so: source/%.f90
	elmerf90 $< -o $@



############################################################################
## Rules for running simulations                                          ##
############################################################################
all: data meshes $(SOLVERS)
helheim: all
	echo elmer/Robin_Beta_Helheim.sif > ELMERSOLVER_STARTINFO ; \
	export glacier=helheim ; \
	nice -n7 mpirun -n 4 ElmerSolver_mpi
kangerd: all
	echo elmer/Robin_Beta_Kangerd.sif > ELMERSOLVER_STARTINFO ; \
	export glacier=kangerd ; \
	nice -n7 mpirun -n 4 ElmerSolver_mpi
jakobshavn: all
	echo elmer/Robin_Beta_Jakobshavn.sif > ELMERSOLVER_STARTINFO ; \
	export glacier=jakobshavn ; \
	nice -n7 mpirun -n 4 ElmerSolver_mpi



############################################################################
## Rules for cleaning up all generated files                              ##
############################################################################
clean:
	rm -rf ExtrudeMesh scripts/*.pyc data/helheim/ data/kangerd/ data/jakobshavn/ dems/helheim/ dems/kangerd/ dems/jakobshavn/ meshes/helheim/*.1* meshes/helheim/*.2* meshes/kangerd/*.1* meshes/kangerd/*.2* meshes/jakobshavn/*.1* meshes/jakobshavn/*.2* meshes/helheim/*.xyz meshes/kangerd/*.xyz meshes/jakobshavn/*.xyz elmer/helheim/ elmer/helheim3d/ elmer/kangerd/ elmer/kangerd3d lib/* *.dat *.out
