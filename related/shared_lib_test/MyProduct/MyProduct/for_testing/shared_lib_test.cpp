#include "MyProduct.h"

#include <vector>
#include <string>
#include <iostream>

#include <fncs.hpp>

int run_main (int argc, const char **argv) {
	if ( !MyProductInitialize() ) {
		std::cerr << "Could not initialize the library properly\n";
		return -1;
	} else {
		try {
			// INITIALIZE FNCS
			


			// Create input dat
			double data[] = {5};
			mwArray aa(1,1,mxDOUBLE_CLASS,mxREAL);
			mwArray bb(1,1,mxDOUBLE_CLASS,mxREAL);
			aa.SetData(data,1); // this copies the data
			bb.SetData(data,1); // this copies the data
	
			// Print the operands
			std::cout << "aa is " << aa << '\n';
			std::cout << "bb is " << bb << '\n';
	
			// Create the output array
			mwArray cc;
	
			// Call the library function
			std::cout << "Calling MyProduct...\n";
			MyProduct(1,cc,aa,bb);
			std::cout << "Returned.\n";
	
			// CRITICAL NOTE: IN c, FREE cc AFTER PROCESSING TO AVOID MEMORY LEAKS
			// mwDestroyArray(cc);
	
			// Print the result
			std::cout << aa << " * " << bb << " = " << cc << '\n';
	
			// Second case:
			mwArray aaa(10);
			mwArray bbb(15);
			std::cout << "Calling MyProduct again...\n";
			MyProduct(1,cc,aaa,bbb);

			// Print the result
			std:: cout << aaa << " * " << bbb << " = " << cc << '\n';


		} catch (const mwException& e) {
			std::cout << "hi\n";
			std::cerr << e.what() << std::endl;
			return -2;
		} catch (...) {
			std::cerr << " Unexpected exception\n";
			return -3;
		}
		// From Integrate a C++ mwArray API Shared Library into an Application:
		// mclTerminateApplication shuts down the MATLAB Runtime.
		// You cannot restart it by calling mclInitializeApplication.
		// Call mclTerminateApplication once and only once in your application.
		mclTerminateApplication();
		return 0;
	}
}

int main (int argc, const char **argv) {
	if (!mclInitializeApplication(nullptr,0)) {
		std::cerr << "Could not initialize application properly\n";
		return -1;
	}
    return mclRunMain(static_cast<mclMainFcnType>(run_main),argc,argv);
}
