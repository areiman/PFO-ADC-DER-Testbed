'''
Supervisor script for PFO-ADC interface test bed
tested using Python 3.6
Author: Andrew Reiman, PNNL
'''

import os		# for system command line access to Julia
# Note: Julia has a C API:
# https://docs.julialang.org/en/release-0.4/manual/embedding/
# This may be appealing in the future for two reasons:
#	1 - It allows variables to be exchanged in memory rather than storrage
#	2 - a C wrapper could be integrated with FNCS in the future


#import matlab						# for MATLAB data types
#import Compiled_MATLAB_ADC_Package	# we will package the compiled MATLAB
# Note: we can relatively easily create a compiled MATLAB Python package
# https://www.mathworks.com/help/compiler_sdk/gs/create-a-python-application-with-matlab-code.html
# https://www.mathworks.com/help/compiler_sdk/python/evaluate-a-compiled-matlab-function.html
#	This package will be specific to the isolated PFO-ADC interface
# Calling a function from c is more complicated but still possible
# https://www.mathworks.com/help/matlab/matlab_external/calling-matlab-software-from-a-c-application.html
# MATLAB-provided example: /extern/examples/eng_mat/engwindemo.c
# 			   or for c++: /extern/examples/eng_mat/engdemo.cpp

# -----------------------------------------------------------------------------
# SUBROUTINES
# -----------------------------------------------------------------------------
def ADC(p_opt,q_opt):
	'''	Simplified ADC: Compute flexibility given control setpoints? '''
	# Future: call compiled matlab here if necessary
	flex_param1_nominal = 70	# flexibility parameters tbd
	flex_param2_nominal = 5		# flexibility parameters tbd
	return flex_param1_nominal,flex_param2_nominal # return default values


# -----------------------------------------------------------------------------
# BEGIN MAIN
# -----------------------------------------------------------------------------
# For this initial implementation, we will assume file IO for the PFO
#	and a static ADC. We will quickly move to a compiled MATLAB Python package
#	or a simple internal Python implementation of an ADC

# INITIALIZE THE ADC outputs
numADCs = 10;				# number of ADCs
flex_param1_nominal = 70	# flexibility parameters tbd
flex_param2_nominal = 5		# flexibility parameters tbd
flex_param1s = numADCs*[flex_param1_nominal]	# array over ADCs
flex_param2s = numADCs*[flex_param2_nominal]	# array over ADCs

# LOOP OVER TIME 
# Note: if data is exchanged at different rates, we will introduce
#	a time manager# Note: persistent data will need to be managed in this supervisor
coordination_time_step_seconds = 600	# 10 minutes
#real_time_step_seconds = 4				# 4 seconds
system_time_seconds = 0;				# initialize
max_system_time_seconds = 3600			# 1 hour

while system_time_seconds <= max_system_time_seconds:
	print("System time: "+str(system_time_seconds)+" seconds")
	
	# -----------
	# Execute PFO
	# -----------
	# call Julia using the system command line, passing runtime parameters
	os.system('echo --- Run Julia Here ---')
	os.system('julia PFO/PFO.jl PFO/data/case24_ieee_rts.m')
	# os.system('PFO_Julia_function.jl persistent_params param1 param2')

#	# read output file(s) written by Julia
#	fh = open('PFO_output.csv','r')
#	lines = []
#	line = fh.readline()
#	while line is not '':
#		lines.append(line)
#	fh.close
	
	# build arrays of parameters to be dispatched to ADCs
	dispatch_Ps = numADCs*[13]		# defaulted to 13
	dispatch_Qs = numADCs*[11]		# defaulted to 11
	
	# print PFO output
	print("PFO output:")
	print(dispatch_Ps)
	print(dispatch_Qs)
	
	# -----------
	# Execute ADC
	# -----------
	# call each ADC
	for idx in range(numADCs):
		flex_param1s[idx],flex_param2s[idx] = ADC(dispatch_Ps,dispatch_Qs)
	
	# print  ADC output
	print("ADC output:")
	print(flex_param1s)
	print(flex_param2s)
	
	# update the system time
	system_time_seconds += coordination_time_step_seconds
	
	print('\n')

# End
