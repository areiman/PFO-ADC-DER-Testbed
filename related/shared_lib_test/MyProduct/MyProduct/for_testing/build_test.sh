rm shared_lib_test
#mbuild MyProduct.cpp shared_lib_test.cpp
mbuild shared_lib_test.cpp MyProduct.so
#g++ -std=c++11 -I /usr/local/MATLAB/MATLAB_Runtime/v91/extern/include/ shared_lib_test.cpp -o shared_lib_test.out

