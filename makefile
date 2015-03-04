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


clean:
	rm -rf ExtrudeMesh scripts/*.pyc data/helheim/ data/kangerd/ data/jakobshavn/ dems/helheim/ dems/kangerd/ dems/jakobshavn/ meshes/helheim/*.1* meshes/helheim/*.2* meshes/kangerd/*.1* meshes/kangerd/*.2* meshes/jakobshavn/*.1* meshes/jakobshavn/*.2* meshes/helheim/*.xyz meshes/kangerd/*.xyz meshes/jakobshavn/*.xyz elmer/helheim/ elmer/helheim3d/ elmer/kangerd/ elmer/kangerd3d lib/* *.dat *.out
