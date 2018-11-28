import sys
#import fncs
import matlab.engine
from matlab import double as MATRIX

import random as rand
from random import gauss


# start MATLAB engine synchronously
print('Starting MATLAB Engine...')
eng = matlab.engine.start_matlab()

#time_stop = int(sys.argv[1])
#time_granted = 0
#op = open (sys.argv[2], "a")


## requires the yaml file
#fncs.initialize()
#print("# time      key       value", file=op)

time_granted = 0
time_stop = 1
while time_granted < time_stop:
#    time_granted = fncs.time_request(time_stop)
	time_granted += 1
	
	# set up and run ADC domain approximation
	adcs = {}
	adcs['adc1'] = {}
	for adc in adcs:
		
		# electric water heaters
		# - heating_element_capacity[kW] -> prated[kW]
		print('Initializing water heaters... ',end='')
		num_ewh = 10
		ewh_name = []
		ewh_prated = []
		ewh_qrated = []
		for idx in range(num_ewh):
			ewh_name.append('EWH_'+str(idx))
			ewh_prated.append(idx+1.0)
			ewh_qrated.append(0.0)
		print('Complete.')

		# hvac systems -- note: powfac <- q = powfac * prated
		# ( ASSUME AIR CONDITIONER ONLY )
		# - design_cooling_capacity[btu/hr]*1[kw]/3412.-[Btu/hr] -> prated[kW]
		# ( ASSUM POWER FACTOR OF 0.85 )
		# - 0.6197 -> powfac
		print('Initializing HVAC systems... ',end='')
		num_ac = 20
		ac_name = []
		ac_prated = []
		ac_powfac = []
		ac_qrated = []
		for idx in range(num_ac):
			ac_name.append('HVAC_'+str(idx))
			ac_prated.append(idx+1.0)
			ac_powfac.append(0.6197)
			ac_qrated.append(0.6197*(idx+1.0))
		print('Complete.')
		print(ac_name)
		print(ac_prated)
		print(ac_powfac)

		# batteries
		# - batt.rated_power -> prated
		# - Binv.rated_power -> invcap
		print('Initializing batteries... ',end='')
		num_batt = 30
		batt_name = []
		batt_prated = []
		batt_invcap = []
		batt_qrated = []
		for idx in range(num_batt):
			batt_name.append('batt_'+str(idx))
			batt_prated.append(idx+1.0)
			batt_invcap.append(idx+1.0)
			batt_qrated.append(idx+1.0)
		print('Complete.')

		# photovoltaics
		# ( Assume that curtailment only affects inverter output )
		# - abs{solar.VA_Out} -> pgenmax
		# - solar.rated_power -> invcap
		print('Initializing photovoltaics... ',end='')
		num_pv = 40
		pv_name = []
		pv_pgenmax = []
		pv_invcap = []
		pv_prated = []
		pv_qrated = []
		for idx in range(num_pv):
			pv_name.append('PV_'+str(idx))
			pv_pgenmax.append(idx+1.0)
			pv_invcap.append(idx+1.0)
			pv_prated.append(idx+1.0)
			pv_qrated.append(idx+1.0)
		print('Complete.')
	
		# Run task 2.1 ADC domain approximation
		# approximate the domian
		eng.eval('help basic_2_1',nargout=0)	
		eng.eval('help basic_2_1_vec',nargout=0)
#		print(eng.isstruct(ewh_pop))
		FandD = eng.basic_2_1_vec(ewh_name,ewh_prated,\
			ac_name,ac_prated,ac_powfac,\
			batt_name,batt_prated,batt_invcap,\
			pv_name,pv_pgenmax,pv_invcap,nargout=2)
		Fadc = FandD[0]
		Dadc = FandD[1]
		print(Fadc)
		print(Dadc)

		# PFO EMULATOR
		# Assuming rectangular flexibility
		rand.seed(None) 	# seed with system time
		tmp = MATRIX([[-1.0,0.0],[0.0,-1.0],[1.0,0.0],[0.0,1.0]])
		print(tmp)
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
		eng.eval('help basic_2_4_ac',nargout=0)
		ewh_state = [1.0]*len(ewh_name)
		ac_state = [0.0]*len(ac_name)
		print (ac_state)
		new_state = eng.basic_2_4_ac(Popt,Qopt,ewh_state,ac_state,\
			ewh_prated,ewh_qrated,ac_prated,ac_qrated,\
			batt_prated,batt_qrated,pv_prated,pv_prated,nargout=6)
		# parse the outputs
		new_ewh_state = new_state[0]
		new_ac_state = new_state[1]
		batt_p = new_state[2]; batt_q = new_state[3];
		pv_p = new_state[4]; pv_q = new_state[5];
		# determine and report the number of EWH on
		ewh_ctr = 0
		ewh_on_ctr = 0
		for idx in range(len(ewh_state)):
			ewh_state[idx] = new_ewh_state[idx][0]
			ewh_ctr += 1
			if ewh_state[idx]:
					ewh_on_ctr += 1
		print(ewh_state)
		print(str(ewh_on_ctr)+" of "+str(ewh_ctr)+\
			" or "+str(ewh_on_ctr/ewh_ctr*100)+"% of ACs are on")
		# determine and report the number of ACs on
		ac_ctr = 0
		ac_on_ctr = 0
		for idx in range(len(ac_state)):
			ac_state[idx] = new_ac_state[idx][0]
			ac_ctr += 1
			if ac_state[idx]:
				ac_on_ctr += 1
		print(ac_state)
		print(str(ac_on_ctr)+" of "+str(ac_ctr)+\
			" or "+str(ac_on_ctr/ac_ctr*100)+"% of ACs are on")
		# report the battery ouput
		print("Battery P: ")
		print(batt_p)
		print("Battery Q: ")
		print(batt_q)
		# report the pv inverter output
		print("PV Inverter P: "+str(pv_p))
		print("PV Inverter Q: "+str(pv_q))






#    a = eng.DummyMAT(SubKeys, nargout=2)
#    key_val = a[1][0]
#    keys = a[0]
#    print("This is returned string from matlab about string", a[0])
#    print("This is returned values from matlab about string", a[1][0])
#    
#    for i in range(len(keys)):
#        fncs.publish(str(keys[i]), key_val[i])	    
#    #fncs.publish(str(topic), power_changed)
     
#fncs.finalize()
