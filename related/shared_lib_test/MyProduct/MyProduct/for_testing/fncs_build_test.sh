echo "Building"
#rm shared_lib_test

#mbuild MyProduct.cpp shared_lib_test.cpp
#mbuild -v shared_lib_test.cpp MyProduct.so

#g++-5 -std=c++11 -I /usr/local/MATLAB/MATLAB_Runtime/v91/extern/include/ shared_lib_test.cpp -o shared_lib_test.out -L /usr/local/MATLAB/MATLAB_Runtime/v91/extern/lib/glnxa64/

mkdir /tmp/MyProduct/

echo "Compiling..."
g++-5 -std=c++11 -c -o /tmp/MyProduct/fncs_shared_lib_test.o -I/usr/local/MATLAB/MATLAB_Runtime/v91/extern/include/ -I $FNCS_INSTALL/include fncs_shared_lib_test.cpp

echo "Linking..."
g++-5 -pthread -Wl,-rpath-link,/usr/local/MATLAB/MATLAB_Runtime/v91/bin/glnxa64 -O /tmp/MyProduct/fncs_shared_lib_test.o MyProduct.so $FNCS_INSTALL/lib/libfncs.so /usr/local/MATLAB/MATLAB_Runtime/v91/sys/os/glnxa64/libstdc++.so.6 -L/usr/local/MATLAB/MATLAB_Runtime/v91/runtime/glnxa64 -lm -lmwmclmcrrt -o fncs_shared_lib_test.out

echo "Cleaning up..."
rm -rf /tmp/MyProduct/

echo "Complete"
