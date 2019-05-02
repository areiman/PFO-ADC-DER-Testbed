import sys
#import fncs
import matlab.engine
from matlab import double as MATRIX

import re

import random as rand
from random import gauss
from random import uniform

from math import sqrt

# for archiving cosim output - especially PFO output
import cosim_archiver as archive


# Start up the matlab engine
eng = matlab.engine.start_matlab()

# These objects will track persistent data
mem = {}
ewh_ranges = {}
ac_ranges = {}
pv_ranges = {}
batt_ranges = {}

# This object will track persistent data
buff = {}
buff['AC_Tdesired'] = {}
buff['AC_P_h'] = {}

def oprint(dat,adc,t,o):
	print("Object:")
	for p in dat[adc][t][o]:
		print("\tdat["+adc+"]["+t+"]["+o+"]["+p+"]: "+str(dat[adc][t][o][p]))

def synch(dat,timestamp=None):
	pub_dat = {}

	eng.eval('addpath ../ADC/test',nargout=0)
#	eng.hello('you',nargout=0)
	eng.eval('addpath ../ADC/ADC_flex',nargout=0)
	eng.eval('addpath ../ADC/ADC_AC',nargout=0)
	eng.eval('addpath ../ADC/ADC_NREL',nargout=0)

	# -------------------------------------------------------------------------
	# PROCESS UPDATE PERSISTENT DATA
	# -------------------------------------------------------------------------
	for adc in dat:
		if not re.search(adc,'NONE'):
			if adc not in mem:
				mem[adc] = {}
				archive.init_adc(adc)
			for t in dat[adc]:
				if t not in mem[adc]:
					mem[adc][t] = {}
				for o in dat[adc][t]:
					if o not in mem[adc][t]:
						mem[adc][t][o] = {}
					for p in dat[adc][t][o]:
						mem[adc][t][o][p] = dat[adc][t][o][p]

	# Store the desired AC temperatures	
	rand.seed(None)
	for adc in dat:
		if adc is not 'ADCNONE':
			for o in dat[adc]['HVAC']:
				if o not in buff['AC_Tdesired']:
#					buff['AC_Tdesired'][o] = dat[adc]['HVAC'][o]['cooling_setpoint']
					# Randomize the desired temperature
					buff['AC_Tdesired'][o] = uniform(65,75)

				

					
	# -------------------------------------------------------------------------
	# ITERATE OVER UPDATED ADCS
	# -------------------------------------------------------------------------
#	print(mem)
	for adc in mem:
		# Initialize the publish object
		pub_dat[adc] = {}
#	if (1):
#		adc = 'M1_ADC12'
		print("\n---------------------------------------")
		print(adc)
		print("---------------------------------------")

		# Set up the water heaters
		t = "WH"
		ewh_names = []
		ewh_prated = []
		ewh_qrated = []
		ewh_state = []
		for o in mem[adc][t]:
			# oprint(mem,adc,t,o)
			ewh_names.append(o)
			ewh_prated.append(mem[adc][t][o]["heating_element_capacity"])
			ewh_qrated.append(0.0)
			ewh_state.append(mem[adc][t][o]["is_waterheater_on"])

		# Set up HVAC systems
		t = "HVAC"
		ac_names = []
		ac_prated = []
		ac_powfac = []
		ac_qrated = []
		ac_temp = []
		ac_heat_set = []
		ac_cool_set = []
		ac_deadband = []
		for o in mem[adc][t]:
			if "heating_setpoint" not in mem[adc][t][o]:
				mem[adc][t][o]["heating_setpoint"] = 65
			if "cooling_setpoint" not in mem[adc][t][o]:
				mem[adc][t][o]["cooling_setpoint"] = 72
			# oprint(mem,adc,t,o)
			ac_names.append(o)
			ac_prated.append(mem[adc][t][o]["design_cooling_capacity"] * 1/3412)
			ac_powfac.append(0.6197)
			ac_qrated.append(0.6197 * ac_prated[-1])
			ac_temp.append(mem[adc][t][o]["air_temperature"])
			ac_heat_set.append(mem[adc][t][o]["heating_setpoint"])
			ac_cool_set.append(mem[adc][t][o]["cooling_setpoint"])
			ac_deadband.append(mem[adc][t][o]["thermostat_deadband"])

		# Set up batteries (o is the inverter)
		t = "BATT"
		batt_names = []
		batt_prated = []
		batt_invcap = []
		batt_qrated = []
		for o in mem[adc][t]:
			# oprint(mem,adc,t,o)
			batt_names.append(o)
			batt_prated.append( mem[adc][t][o]["battery.rated_power"] / 1000 )
			batt_invcap.append( mem[adc][t][o]["inverter.rated_power"] / 1000 )
			batt_qrated.append( mem[adc][t][o]["battery.rated_power"] / 1000 )

		# Set up PV systems (o is the inverter)
		t = "PV"
		pv_names = []
		pv_pgenmax = []
		pv_invcap = []
		pv_prated = []
		pv_qrated = []
		for o in mem[adc][t]:
			# oprint(mem,adc,t,o)
			pv_names.append(o)
			pv_pgenmax.append( mem[adc][t][o]["solar.rated_power"] / 1000 )
			pv_invcap.append( mem[adc][t][o]["solar.rated_power"] / 1000 )
			pv_prated.append( mem[adc][t][o]["solar.rated_power"] / 1000 )
			pv_qrated.append( mem[adc][t][o]["solar.rated_power"] / 1000 )


		# Run task 2.1 ADC domain approximation
#		eng.eval('help basic_2_1',nargout=0)
#		eng.eval('help basic_2_1_vec',nargout=0)
#		FandD = eng.basic_2_1_vec(ewh_names,ewh_prated,\
#			ac_names,ac_prated,ac_powfac,\
#			batt_names,batt_prated,batt_invcap,\
#			pv_names,pv_pgenmax,pv_invcap,nargout=2)

		print("Device totals:")
		print("    {} electric water heaters".format(len(ewh_names)))
		print("    {} air conditioners".format(len(ac_names)))
		print("    {} photovoltaic systems".format(len(pv_names)))
		print("    {} battery systems".format(len(batt_names)))
		# print(ewh_names)
		# print(ac_names)
		# print(pv_names)
		# print(batt_names)
		flex_agg = eng.testbed_2_1_vec(ewh_names,ewh_prated,\
			ac_names,ac_prated,ac_powfac,\
			batt_names,batt_prated,batt_invcap,\
			pv_names,pv_pgenmax,pv_invcap,nargout=6)
		Fadc = flex_agg[0]
		Dadc = flex_agg[1]
		ewh_range = flex_agg[2]
		ac_range = flex_agg[3]
		pv_range = flex_agg[4]
		batt_range = flex_agg[5]
#		print("Fadc is: "+str(Fadc))
#		print("Dadc is: "+str(Dadc))
#		print("Ranges:")
#		print(ewh_range)
#		print(ac_range)
#		print(pv_range)
#		print(batt_range)

		ewh_ranges[adc] = ewh_range
		ac_ranges[adc] = ac_range
		pv_ranges[adc] = pv_range
		batt_ranges[adc] = batt_range
		
		
		# ---------------------------------------------------------------------
		# PFO EMULATOR
		# ---------------------------------------------------------------------
		# Assuming rectangular flexibility
		rand.seed(None) 	# seed with system time
#		tmp = MATRIX([[-1.0,0.0],[0.0,-1.0],[1.0,0.0],[0.0,1.0]])
#		print(tmp)
		if Fadc[0][0] == -1.0 and Fadc[0][1] == 0.0 \
				and Fadc[1][0] == 0.0 and Fadc[1][1] == -1.0 \
				and Fadc[2][0] == 1.0 and Fadc[2][1] == 0.0 \
				and Fadc[3][0] == 0.0 and Fadc[3][1] == 1.0:
			Popt = ( Dadc[0][0] + Dadc[2][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
			if Popt > Dadc[0][0]:
				Popt = Dadc[0][0]
			if Popt < -1*Dadc[2][0]:
				Popt = -1*Dadc[2][0]
			Qopt = ( Dadc[1][0] + Dadc[3][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
			if Qopt > Dadc[1][0]:
				Qopt = Dadc[1][0]
			if Qopt < -1*Dadc[3][0]:
				Qpot = -1*Dadc[3][0]
		elif Fadc[0][0] == 1.0 and Fadc[0][1] == 0.0 \
				and Fadc[1][0] == -1.0 and Fadc[1][1] == 0.0 \
				and Fadc[2][0] == 0.0 and Fadc[2][1] == 1.0 \
				and Fadc[3][0] == 0.0 and Fadc[3][1] == -1.0:
			Popt = ( Dadc[0][0] + Dadc[1][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
			if Popt > Dadc[0][0]:
				Popt = Dadc[0][0]
			if Popt < -1*Dadc[1][0]:
				Popt = -1*Dadc[1][0]
			Qopt = ( Dadc[2][0] + Dadc[3][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
			if Qopt > Dadc[2][0]:
				Qopt = Dadc[2][0]
			if Qopt < -1*Dadc[3][0]:
				Qopt = -1*Dadc[3][0]
		else:
			print("Error: unexpected Fadc")
			exit()
		print("Popt is "+str(Popt))
		print("Qopt is "+str(Qopt))

		
		# ----------------------------------------------------------------------
		# DISAGGREGATION
		# ----------------------------------------------------------------------
		eng.eval('addpath ../ADC/ADC_flex/functions',nargout=0)
		disagg_dispatch = eng.disaggregation(MATRIX([[Popt,Qopt]]),\
			ewh_ranges[adc],ac_ranges[adc],pv_ranges[adc],batt_ranges[adc],\
			nargout=4)

		Popt_ewh = disagg_dispatch[0][0][0]
		Qopt_ewh = disagg_dispatch[0][0][1]
		print("    Popt_ewh is: "+str(Popt_ewh))
		print("    Qopt_ewh is: "+str(Qopt_ewh))
		Popt_ac = disagg_dispatch[1][0][0]
		Qopt_ac = disagg_dispatch[1][0][1]
		print("    Popt_ac is: "+str(Popt_ac))
		print("    Qopt_ac is: "+str(Qopt_ac))
		Popt_pv = disagg_dispatch[2][0][0]
		Qopt_pv = disagg_dispatch[2][0][1]
		print("    Popt_pv is: "+str(Popt_pv))
		print("    Qopt_pv is: "+str(Qopt_pv))
		Popt_batt = disagg_dispatch[3][0][0]
		Qopt_batt = disagg_dispatch[3][0][1]
		print("    Popt_batt is: "+str(Popt_batt))
		print("    Qopt_batt is: "+str(Qopt_batt))

		# ----------------------------------------------------------------------
		# ARCHIVE AGGREGATE AND DISAGGREGATED PFO OUTPUT
		# ----------------------------------------------------------------------
		archive.archive_pfo(adc,timestamp,Popt,Qopt,\
			Popt_ewh,Qopt_ewh,Popt_ac,\
			Qopt_ac,Popt_pv,Qopt_pv,Popt_batt,Qopt_batt)
#		archive.archive_pfo(adc,timestamp,Popt,Qopt)


		"""
		# ----------------------------------------------------------------------
		# DUMMY TASK 2.4 - DER DISPATCH
		# ----------------------------------------------------------------------
		# Call the dummy task 2.4 code
		new_state = eng.basic_2_4(Popt,Qopt,ewh_state,\
			ac_temp,ac_heat_set,ac_cool_set,ac_deadband,\
			ewh_prated,ewh_qrated,ac_prated,ac_qrated,\
			batt_prated,batt_qrated,pv_prated,pv_prated,nargout=7)
		# parse the outputs
		new_ewh_tank_setpoint = new_state[0]
		new_ac_heat_set = new_state[1]
		new_ac_cool_set = new_state[2]
		batt_p = new_state[3]; batt_q = new_state[4];
		pv_p = new_state[5]; pv_q = new_state[6];

		# print(new_state)
	
		# Populate water heaters in the publish object
		t = "WH"
		pub_dat[adc][t] = {}
		# print(new_ewh_tank_setpoint)
		if len(ewh_names) == 1:
			o = ewh_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint
		else:
			for idx in range(len(ewh_names)):
				# print('\t'+str(idx))
				o = ewh_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint[idx][0]

		# Populate the HVACs in the publish object
		t = "HVAC"
		pub_dat[adc][t] = {}
		if len(ac_names) == 1:
			o = ac_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["cooling_setpoint"] = new_ac_cool_set
			pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set
		else:
			for idx in range(len(ac_names)):
				o = ac_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["cooling_setpoint"] = new_ac_cool_set[idx][0]
				pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set[idx][0]

		# Populate the battery inverters in the publish object
		t = "BATT"
		pub_dat[adc][t] = {}
		# print(batt_p)
		if len(batt_names) == 1:
			o = batt_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = batt_p
			pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q
		else:
			for idx in range(len(batt_names)):
				# print('\t'+str(idx))
				o = batt_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = batt_p[idx][0]
				pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q[idx][0]

		# Populate the PV inverters
		t = "PV"
		pub_dat[adc][t] = {}
		# print('\t'+str(pv_p))
		if len(pv_names) == 1:
			o = pv_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = pv_p
			pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q
		else:
			for idx in range(len(pv_names)):
				# print(idx)
				o = pv_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = pv_p[idx][0]
				pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q[idx][0]	
		"""
		
		
		# ---------------------------------------------------------------------
		# DER DISPATCH FOR EWH
		# ---------------------------------------------------------------------
		# To be taken from dummy implementation

		'''
		# Populate water heaters in the publish object
		t = "WH"
		pub_dat[adc][t] = {}
		# print(new_ewh_tank_setpoint)
		if len(ewh_names) == 1:
			o = ewh_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint
		else:
			for idx in range(len(ewh_names)):
				# print('\t'+str(idx))
				o = ewh_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint[idx][0]
		'''

		# ----------------------------------------------------------------------
		# DER DISPATCH FOR HVAC
		# ----------------------------------------------------------------------
		# Set up inputs
		Q_ref = Popt_ac 
		para_Tmin = []
		para_Tmax = []
		para_Tdesired = []
		para_ratio = []
		para_power = []
		para_C_a = []
		para_C_m = []
		para_H_m = []
		para_U_A = []
		para_mass_internal_gain_fraction = []
		para_mass_solar_gain_fraction = []

		Q_h = []
		Q_i = []
		Q_s = []
		Dtemp = []
		halfband = []
		Dstatus = []
		P_h = []
		P_cap = 0
		mdt = 0
		T_out = 0

		t = 'HVAC'
		for o in mem[adc][t]:

			# para is a structure of vectors

			# To be randomized?
			para_Tmin.append(65)
			para_Tmax.append(75)

			# initial 'cooling_setpoint'
#			para['Tdesired'].append(buff['AC_Tdesired'][o])
			para_Tdesired.append(mem[adc][t][o]['cooling_setpoint'])

			# [0.5 to 15] uniform distribution -- to be randomized
			para_ratio.append(1.0)

			# hvac_load
			para_power.append(mem[adc][t][o]['hvac_load'])

			para_C_a.append(mem[adc][t][o]['air_heat_capacity'])
			para_C_m.append(mem[adc][t][o]['mass_heat_capacity'])
			para_H_m.append(mem[adc][t][o]['mass_heat_coeff'])
			para_U_A.append(mem[adc][t][o]['UA'])

			# Are these two part of the interface?
			para_mass_internal_gain_fraction.\
				append(mem[adc][t][o]['mass_internal_gain_fraction'])
			para_mass_solar_gain_fraction.\
				append(mem[adc][t][o]['mass_solar_gain_fraction'])

			# These two exist
			Q_h.append(mem[adc][t][o]['Qh'])
			Q_i.append(mem[adc][t][o]['Qi'])

			# vector of calculated values
			Q_s.append(mem[adc][t][o]['incident_solar_radiation'] *\
				mem[adc][t][o]['solar_heatgain_factor'])

			# This is a list/vector of [ air_temperature , mass_temperature ]
			Dtemp.append([])
			Dtemp[-1].append( mem[adc][t][o]['air_temperature'] )
			Dtemp[-1].append( mem[adc][t][o]['mass_temperature'] )

			halfband.append( mem[adc][t][o]['thermostat_deadband'] / 2.0 )

			# Device status? what are the options? how do we know? historical term?
			# should be mem[adc][t][o]['is_COOL_on'] (new parameter)a
			if mem[adc][t][o]['is_COOL_on']:
				Dstatus.append('ON')
			else:
				Dstatus.append('OFF')

			# T_out is the outside temperature - same for all houses
			if T_out:
				if T_out != mem[adc][t][o]['outdoor_temperature']:
					print("WARNING: T_out is not he same for all houses")
			else:
				T_out = mem[adc][t][o]['outdoor_temperature']


#		# Test the struct of vectors
#		eng.PrintStructVec(para,nargout=0)
#		sys.exit()

		# Historical power - vector of past 24 hours @ 5 minutes
		P_h = (24*12*[0.07])


		# P_cap scalar price units /[$/kW] -> 1 for $/kW; 1000 for $/MW
		P_cap = 1

		# Market period in hours (@5-min)
		mdt = 1/3600*300

		# Call the AC-based task 2.4 code
#		out = eng.Task_2_4_PNNL(Q_ref,para,\
#			Q_h,Q_i,Q_s,Dtemp,halfband,Dstatus,P_h,P_cap,mdt,nargout=2)
		# Parse outputs from the ac-based task 2.4 code
#		T_set = out[0]
#		P_h = out[1]
		out = eng.Task_2_4_PNNL_vec(Q_ref,\
			para_Tmin,para_Tmax,para_Tdesired,para_ratio,para_power,\
			para_C_a,para_C_m,para_H_m,para_U_A,\
			para_mass_internal_gain_fraction,para_mass_solar_gain_fraction,\
			Q_h,Q_i,Q_s,Dtemp,halfband,Dstatus,P_h,P_cap,mdt,T_out,nargout=2)
		
		T_set = out[0]
		P_h = out[0]
		
		sys.exit()

		# ----------------------------------------------------------------------
		# TASK 2.4 FOR PV AND BATTERIES
		# ----------------------------------------------------------------------
		
		# Control time
		deltat = 30

		# Number of PV-inverters and bettery inverters under control
		n_pv = 10
		n_ba = 12

		# PV capacity
		cap_pv =\
			 [4410.43,4480.22,4381.46,4462.06,4401.66,\
			 4439.82,4425.14,4429.96,4495.07,4506.36]

		# PV available power
#		pv_av = 

		# Call the PV and Battery implementation of task 2.4
		eng.eval('ADC_20180815',nargout=0)
	

	# --------------------------------------------------------------------------
	# RETURN THE THE PUBLISH OBJECT BACK TO THE PARSER 
	# --------------------------------------------------------------------------
	return pub_dat

