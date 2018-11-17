import sys
#import fncs
import matlab.engine
from matlab import double as MATRIX

import random as rand
from random import gauss

from math import sqrt

# Start up the matlab engine
eng = matlab.engine.start_matlab()

# This object will track persistent data
mem = {}

def oprint(dat,adc,t,o):
	print("Object:")
	for p in dat[adc][t][o]:
		print("\tdat["+adc+"]["+t+"]["+o+"]["+p+"]: "+str(dat[adc][t][o][p]))

def synch(dat):
	pub_dat = {}
	
	# -------------------------------------------------------------------------
	# ITERATE OVER ADCS
	# -------------------------------------------------------------------------
	for adc in dat:
		if adc not in mem:
			mem[adc] = {}
			mem[adc]["WH"] = {}
			mem[adc]["HVAC"] = {}
			mem[adc]["BATT"] = {}
			mem[adc]["PV"] = {}
		
		# Set up the water heaters
		t = "WH"
		ewh_names = []
		ewh_prated = []
		ewh_qrated = []
		ewh_state = []
		for o in dat[adc][t]:
			oprint(dat,adc,t,o)
			ewh_names.append(o)
			ewh_prated.append(dat[adc][t][o]["heating_element_capacity"])
			ewh_qrated.append(0.0)
			ewh_state.append(dat[adc][t][o]["is_waterheater_on"])

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
		for o in dat[adc][t]:
			if o not in mem[adc][t]:
				mem[adc][t][o] = {}
				mem[adc][t][o]["heating_setpoint"] = 65
				mem[adc][t][o]["cooling_setpoint"] = 72
			oprint(dat,adc,t,o)
			ac_names.append(o)
			ac_prated.append(dat[adc][t][o]["design_cooling_capacity"] * 1/3412)
			ac_powfac.append(0.6197)
			ac_qrated.append(0.6197 * ac_prated[-1])
			ac_temp.append(dat[adc][t][o]["air_temperature"])
			ac_heat_set.append(mem[adc][t][o]["heating_setpoint"])
			ac_cool_set.append(mem[adc][t][o]["cooling_setpoint"])
			ac_deadband.append(dat[adc][t][o]["thermostat_deadband"])

		# Set up batteries (o is the inverter)
		t = "BATT"
		batt_names = []
		batt_prated = []
		batt_invcap = []
		batt_qrated = []
		for o in dat[adc][t]:
			oprint(dat,adc,t,o)
			batt_names.append(o)
			batt_prated.append(dat[adc][t][o]["battery.rated_power"])
			batt_invcap.append(dat[adc][t][o]["inverter.rated_power"])
			batt_qrated.append(dat[adc][t][o]["battery.rated_power"])

		# Set up PV systems (o is the inverter)
		t = "PV"
		pv_names = []
		pv_pgenmax = []
		pv_invcap = []
		pv_prated = []
		pv_qrated = []
		for o in dat[adc][t]:
			oprint(dat,adc,t,o)
			pv_names.append(o)
			pv_pgenmax.append(dat[adc][t][o]["solar.rated_power"])
			pv_invcap.append(dat[adc][t][o]["solar.rated_power"])
			pv_prated.append(dat[adc][t][o]["solar.rated_power"])
			pv_qrated.append(dat[adc][t][o]["solar.rated_power"])


		# Run task 2.1 ADC domain approximation
		eng.eval('help basic_2_1',nargout=0)
		eng.eval('help basic_2_1_vec',nargout=0)
		FandD = eng.basic_2_1_vec(ewh_names,ewh_prated,\
			ac_names,ac_prated,ac_powfac,\
			batt_names,batt_prated,batt_invcap,\
			pv_names,pv_pgenmax,pv_invcap,nargout=2)
		Fadc = FandD[0]
		Dadc = FandD[1]


		# PFO EMULATOR
		# Assuming rectangular flexibility
		rand.seed(None) 	# seed with system time
#		tmp = MATRIX([[-1.0,0.0],[0.0,-1.0],[1.0,0.0],[0.0,1.0]])
#		print(tmp)
		if Fadc[0][0] == -1.0 and Fadc[0][1] == 0.0 \
				and Fadc[1][0] == 0.0 and Fadc[1][1] == -1.0 \
				and Fadc[2][0] == 1.0 and Fadc[2][1] == 0.0 \
				and Fadc[3][0] == 0.0 and Fadc[3][1] == 1.0:
			Popt = ( Dadc[0][0] + Dadc[2][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
			Qopt = ( Dadc[1][0] + Dadc[3][0] ) / 2.0 * ( 1 + gauss(0,1)/3.0 )
		else:
			print("unexpected Fadc")
			Popt = 0
			Qopt = 0
		print("Popt is "+str(Popt))
		print("Qopt is "+str(Qopt))

		# Call the dummy task 2.4 code
		eng.eval('help basic_2_4',nargout=0)
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

		print(new_state)

		
		# BUILD THE PUBLISH DATA STRUCTURE
		pub_dat[adc] = {}
	
		# Populate water heaters
		t = "WH"
		pub_dat[adc][t] = {}
		print(new_ewh_tank_setpoint)
		if len(ewh_names) == 1:
			o = ewh_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint
		else:
			for idx in range(len(ewh_names)):
				print('\t'+str(idx))
				o = ewh_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint[idx][0]

		# Populate the HVACs
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

		# Populate the battery inverters
		t = "BATT"
		pub_dat[adc][t] = {}
		print(batt_p)
		if len(batt_names) == 1:
			o = batt_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = batt_p
			pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q
		else:
			for idx in range(len(batt_names)):
				print('\t'+str(idx))
				o = batt_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = batt_p[idx][0]
				pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q[idx][0]

		# Populate the PV inverters
		t = "PV"
		pub_dat[adc][t] = {}
		print('\t'+str(pv_p))
		if len(pv_names) == 1:
			o = pv_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = pv_p
			pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q
		else:
			for idx in range(len(pv_names)):
				print(idx)
				o = pv_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = pv_p[idx][0]
				pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q[idx][0]

	return pub_dat

