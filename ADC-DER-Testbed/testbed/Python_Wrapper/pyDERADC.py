import sys;
#import fncs;
import matlab.engine

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
		num_ewh = 1
		ewh_name = []
		ewh_prated = []
		for idx in range(num_ewh):
			ewh_name.append('EWH_'+str(idx))
			ewh_prated.append(idx+1)
		print('Complete.')

		# hvac systems -- note: powfac <- q = powfac * prated
		# ( ASSUME AIR CONDITIONER ONLY )
		# - design_cooling_capacity[btu/hr]*1[kw]/3412.-[Btu/hr] -> prated[kW]
		# ( ASSUM POWER FACTOR OF 0.85 )
		# - 0.6197 -> powfac
		print('Initializing HVAC systems... ',end='')
		num_ac = 2
		ac_name = []
		ac_prated = []
		ac_powfac = []
		for idx in range(num_ac):
			ac_name.append('HVAC_'+str(idx))
			ac_prated.append(idx+1)
			ac_powfac.append(0.6197)
		print('Complete.')

		# batteries
		# - batt.rated_power -> prated
		# - Binv.rated_power -> invcap
		print('Initializing batteries... ',end='')
		num_batt = 3
		batt_name = []
		batt_prated = []
		batt_invcap = []
		for idx in range(num_batt):
			batt_name.append('batt_'+str(idx))
			batt_prated.append(idx+1)
			batt_invcap.append(idx+1)
		print('Complete.')

		# photovoltaics
		# ( Assume that curtailment only affects inverter output )
		# - abs{solar.VA_Out} -> pgenmax
		# - solar.rated_power -> invcap
		print('Initializing photovoltaics... ',end='')
		num_pv = 4
		pv_name = []
		pv_pgenmax = []
		pv_invcap = []
		for idx in range(num_pv):
			pv_name.append('PV_'+str(idx))
			pv_pgenmax.append(idx+1)
			pv_invcap.append(idx+1)
		print('Complete.')
	
		# Run task 2.1 ADC domain approximation
		# approximate the domian
		eng.eval('help basic_2_1',nargout=0)	
#		print(eng.isstruct(ewh_pop))
		result = eng.basic_2_1_vec(ewh_name,ewh_prated,\
			ac_name,ac_prated,ac_powfac,\
			batt_name,batt_prated,batt_invcap,\
			pv_name,pv_pgenmax,pv_invcap,nargout=2)
		Fadc = result[0]
		Dadc = result[1]
		print(Fadc)
		print(Dadc)

		# PFO EMULATOR
		# Assuming rectangular flexibility
		tmp = matlab.double([[-1.0,0.0],[0.0,-1.0],[1.0,0.0],[0.0,1.0]])
		if isinstance(Fadc,(list,)):
			print("Fadc is list")
		if isinstance (tmp,(list,)):
			print("tmp is list")
		print(tmp)
		if Fadc[0][0] == -1.0 and Fadc[0][1] == 0.0 \
				and Fadc[1][0] == 0.0 and Fadc[1][1] == -1.0 \
				and Fadc[2][0] == 1.0 and Fadc[2][1] == 0.0 \
				and Fadc[3][0] == 0.0 and Fadc[3][1] == 1.0:
			print("hi")
			Popt = ( Dadc[0][0] + Dadc[2][0] ) / 2.0
			Qopt = ( Dadc[1][0] + Dadc[3][0] ) / 2.0
		else:
			print("unexpected Fadc")
			Popt = 0
			Qopt = 0
		print("Popt is "+str(Popt))
		print("Qopt is "+str(Qopt))

		# Call the dummy task 2.4 code




#		eng.ADC_20180815(nargout=0)


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
