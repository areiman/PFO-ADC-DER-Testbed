//
// MATLAB Compiler: 6.3 (R2016b)
// Date: Thu May  3 18:46:30 2018
// Arguments: "-B" "macro_default" "-W" "cpplib:MyProduct" "-T" "link:lib" "-d"
// "/home/areiman/PFO-ADC-DER-Testbed/related/shared_lib_test/MyProduct/MyProduc
// t/for_testing" "-v"
// "/home/areiman/PFO-ADC-DER-Testbed/related/shared_lib_test/MyProduct/MyProduc
// t.m" 
//

#include <stdio.h>
#define EXPORTING_MyProduct 1
#include "MyProduct.h"

static HMCRINSTANCE _mcr_inst = NULL;


#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultPrintHandler(const char *s)
{
  return mclWrite(1 /* stdout */, s, sizeof(char)*strlen(s));
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultErrorHandler(const char *s)
{
  int written = 0;
  size_t len = 0;
  len = strlen(s);
  written = mclWrite(2 /* stderr */, s, sizeof(char)*len);
  if (len > 0 && s[ len-1 ] != '\n')
    written += mclWrite(2 /* stderr */, "\n", sizeof(char));
  return written;
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_MyProduct_C_API
#define LIB_MyProduct_C_API /* No special import/export declaration */
#endif

LIB_MyProduct_C_API 
bool MW_CALL_CONV MyProductInitializeWithHandlers(
    mclOutputHandlerFcn error_handler,
    mclOutputHandlerFcn print_handler)
{
    int bResult = 0;
  if (_mcr_inst != NULL)
    return true;
  if (!mclmcrInitialize())
    return false;
    {
        mclCtfStream ctfStream = 
            mclGetEmbeddedCtfStream((void *)(MyProductInitializeWithHandlers));
        if (ctfStream) {
            bResult = mclInitializeComponentInstanceEmbedded(   &_mcr_inst,
                                                                error_handler, 
                                                                print_handler,
                                                                ctfStream);
            mclDestroyStream(ctfStream);
        } else {
            bResult = 0;
        }
    }  
    if (!bResult)
    return false;
  return true;
}

LIB_MyProduct_C_API 
bool MW_CALL_CONV MyProductInitialize(void)
{
  return MyProductInitializeWithHandlers(mclDefaultErrorHandler, mclDefaultPrintHandler);
}

LIB_MyProduct_C_API 
void MW_CALL_CONV MyProductTerminate(void)
{
  if (_mcr_inst != NULL)
    mclTerminateInstance(&_mcr_inst);
}

LIB_MyProduct_C_API 
void MW_CALL_CONV MyProductPrintStackTrace(void) 
{
  char** stackTrace;
  int stackDepth = mclGetStackTrace(&stackTrace);
  int i;
  for(i=0; i<stackDepth; i++)
  {
    mclWrite(2 /* stderr */, stackTrace[i], sizeof(char)*strlen(stackTrace[i]));
    mclWrite(2 /* stderr */, "\n", sizeof(char)*strlen("\n"));
  }
  mclFreeStackTrace(&stackTrace, stackDepth);
}


LIB_MyProduct_C_API 
bool MW_CALL_CONV mlxMyProduct(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
  return mclFeval(_mcr_inst, "MyProduct", nlhs, plhs, nrhs, prhs);
}

LIB_MyProduct_CPP_API 
void MW_CALL_CONV MyProduct(int nargout, mwArray& c, const mwArray& a, const mwArray& b)
{
  mclcppMlfFeval(_mcr_inst, "MyProduct", nargout, 1, 2, &c, &a, &b);
}

