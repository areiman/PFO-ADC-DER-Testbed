CPPFLAGS = -I$(FNCS_INSTALL)/include
LDFLAGS = -L$(FNCS_INSTALL)/lib
LIBS = -lfncs -lczmq -lzmq

all: simDERADC

simDERADC: simDERADC.cpp
	$(CXX) simDERADC.cpp -o simDERADC $(CPPFLAGS) $(LDFLAGS) $(LIBS)

clean:
	rm -f simDERADC *.out *.log *.txt
