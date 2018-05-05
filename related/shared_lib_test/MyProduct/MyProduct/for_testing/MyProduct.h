//
// MATLAB Compiler: 6.3 (R2016b)
// Date: Thu May  3 18:46:30 2018
// Arguments: "-B" "macro_default" "-W" "cpplib:MyProduct" "-T" "link:lib" "-d"
// "/home/areiman/PFO-ADC-DER-Testbed/related/shared_lib_test/MyProduct/MyProduc
// t/for_testing" "-v"
// "/home/areiman/PFO-ADC-DER-Testbed/related/shared_lib_test/MyProduct/MyProduc
// t.m" 
//

#ifndef __MyProduct_h
#define __MyProduct_h 1

#if defined(__cplusplus) && !defined(mclmcrrt_h) && defined(__linux__)
#  pragma implementation "mclmcrrt.h"
#endif
#include "mclmcrrt.h"
#include "mclcppclass.h"
#ifdef __cplusplus
extern "C" {
#endif

#if defined(__SUNPRO_CC)
/* Solaris shared libraries use __global, rather than mapfiles
 * to define the API exported from a shared library. __global is
 * only necessary when building the library -- files including
 * this header file to use the library do not need the __global
 * declaration; hence the EXPORTING_<library> logic.
 */

#ifdef EXPORTING_MyProduct
#define PUBLIC_MyProduct_C_API __global
#else
#define PUBLIC_MyProduct_C_API /* No import statement needed. */
#endif

#define LIB_MyProduct_C_API PUBLIC_MyProduct_C_API

#elif defined(_HPUX_SOURCE)

#ifdef EXPORTING_MyProduct
#define PUBLIC_MyProduct_C_API __declspec(dllexport)
#else
#define PUBLIC_MyProduct_C_API __declspec(dllimport)
#endif

#define LIB_MyProduct_C_API PUBLIC_MyProduct_C_API


#else

#define LIB_MyProduct_C_API

#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_MyProduct_C_API 
#define LIB_MyProduct_C_API /* No special import/export declaration */
#endif

extern LIB_MyProduct_C_API 
bool MW_CALL_CONV MyProductInitializeWithHandlers(
       mclOutputHandlerFcn error_handler, 
       mclOutputHandlerFcn print_handler);

extern LIB_MyProduct_C_API 
bool MW_CALL_CONV MyProductInitialize(void);

extern LIB_MyProduct_C_API 
void MW_CALL_CONV MyProductTerminate(void);



extern LIB_MyProduct_C_API 
void MW_CALL_CONV MyProductPrintStackTrace(void);

extern LIB_MyProduct_C_API 
bool MW_CALL_CONV mlxMyProduct(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);


#ifdef __cplusplus
}
#endif

#ifdef __cplusplus

/* On Windows, use __declspec to control the exported API */
#if defined(_MSC_VER) || defined(__BORLANDC__)

#ifdef EXPORTING_MyProduct
#define PUBLIC_MyProduct_CPP_API __declspec(dllexport)
#else
#define PUBLIC_MyProduct_CPP_API __declspec(dllimport)
#endif

#define LIB_MyProduct_CPP_API PUBLIC_MyProduct_CPP_API

#else

#if !defined(LIB_MyProduct_CPP_API)
#if defined(LIB_MyProduct_C_API)
#define LIB_MyProduct_CPP_API LIB_MyProduct_C_API
#else
#define LIB_MyProduct_CPP_API /* empty! */ 
#endif
#endif

#endif

extern LIB_MyProduct_CPP_API void MW_CALL_CONV MyProduct(int nargout, mwArray& c, const mwArray& a, const mwArray& b);

#endif
#endif
