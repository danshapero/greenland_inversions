.PHONY: clean


ExtrudeMesh: ExtrudeMesh.c
	gcc ExtrudeMesh.c -o ExtrudeMesh -lm

_SOURCES=Init.f90 Interp.f90
SOURCES = $(patsubst %,source/%,$(_SOURCES))

_SOLVERS=$(_SOURCES:.f90=.so)
SOLVERS=$(patsubst %,lib/%,$(_SOLVERS)) 

lib/%.so: source/%.f90
	elmerf90 $< -o $@

all: ExtrudeMesh $(SOLVERS)
#helheim: all
#	echo elmer/Robin_Beta_Helheim.sif > ELMERSOLVER_STARTINFO ; \
#	export glacier=helheim ; \
#	nice -n7 mpirun -n 4 ElmerSolver_mpi
#kangerd: all
#	echo elmer/Robin_Beta_Kangerd.sif > ELMERSOLVER_STARTINFO ; \
#	export glacier=kangerd ; \
#	nice -n7 mpirun -n 4 ElmerSolver_mpi
#jakobshavn: all
#	echo elmer/Robin_Beta_Jakobshavn.sif > ELMERSOLVER_STARTINFO ; \
#	export glacier=jakobshavn ; \
#	nice -n7 mpirun -n 4 ElmerSolver_mpi


clean:
	rm -rf ExtrudeMesh scripts/*.pyc data/helheim/ data/kangerd/ data/jakobshavn/ dems/helheim/ dems/kangerd/ dems/jakobshavn/ meshes/helheim/*.1* meshes/helheim/*.2* meshes/kangerd/*.1* meshes/kangerd/*.2* meshes/jakobshavn/*.1* meshes/jakobshavn/*.2* meshes/helheim/*.xyz meshes/kangerd/*.xyz meshes/jakobshavn/*.xyz elmer/helheim/ elmer/helheim3d/ elmer/kangerd/ elmer/kangerd3d lib/* *.dat *.out
