############################ -*- Mode: Makefile -*- ###########################
## Makefile ---
##
## Auteur          : Jalel Chergui (LIMSI-CNRS) <Jalel.Chergui@limsi.fr>
## Créé le         : Wed Mar  1 10:21:39 2006
## Dern. mod. par  : Jalel Chergui (LIMSI-CNRS) <Jalel.Chergui@limsi.fr>
## Dern. mod. le   : Wed Jan  4 13:36:20 2012
###############################################################################

SOURCE = $(HOME)/BLUE-SOURCE
VERSION = BLUE-11.2
BLUEDIR = $(SOURCE)/$(VERSION)

include $(BLUEDIR)/options/Make.inc

SHELL   = /bin/bash
CMD     = aeration.x
SRCS	= aeration.f90
OBJS	= aeration.o
NP	= 1

FCFLAGS = $(FFLAGS) -I. -I$(BLUEINC)
LIBS	= $(BLUELIB)

.SUFFIXES: .f90 .o

all: $(CMD)

$(OBJS): $(BLUELIB)

.f90.o : *.f90
	$(FC) $(FCFLAGS) -c $<

$(CMD):	$(OBJS)
	$(FC) $(LDFLAGS) -o $(@) $(OBJS) $(LIBS)

exe : $(CMD)
	mpirun -wd $(PWD) -np $(NP) ./$(CMD)
	env DYLD_LIBRARY_PATH=/opt/local/vtk/lib vtk2xml.py -b -n *.vtk && rm -f *.vtk

clean:;	rm -f $(OBJS) *.mod core* $(CMD)

cleanall:; make clean; rm -f *.vt* *.pvd INT_*.stl *.rst *.csv *~
