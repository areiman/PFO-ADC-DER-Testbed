'''fncs_parser'''

import re

import ADC_Manager

# defining this here will keep it in memory when this module is imported
dat = {}

def synch(keys,vals,timestamp=None):
	if len(keys) != len(vals):
		print("ERROR: number of keys does not equal number of values")
		return None
	
	# UPDATE the to_ADC structure
	for idx in range(len(keys)):
		# parse the key
		key = keys[idx]
#		print(key)
		# m = re.match('(M[^_]+_ADC[^_]+)_(.+?_tm)_(\S+)',key)
		m = re.search('(M[^_]+_ADC[^_]+)_(.+?_tm)_(\S+)', key)
		adc = m.group(1)
		der = m.group(2)
		param = m.group(3)

#		print(adc)
#		print(der)
#		print(param)

		# if the value contains a single float, extract it
		val = vals[idx]
		m = re.search('[^\d\.-]*(-?\d+\.?\d*|-?\d*\.?\d+)[^\d\.-]*',val)
		if m:
			val = float(m.group(1))
		
		# create the adc if it doesn't exist yet
		if adc not in dat:
			dat[adc] = {}
			dat[adc]["WH"] = {}
			dat[adc]["HVAC"] = {}
			dat[adc]["BATT"] = {}
			dat[adc]["PV"] = {}

		# UPDATE THE TO_ADCS OBJECT BASED ON THE DER TYPE

		if re.match('house',der):
			# this applies to both WH and HVAC
			if re.match('house\d+_wh',der):
				# water heater
				if der not in dat[adc]["WH"]:
					dat[adc]["WH"][der] = {}
				dat[adc]["WH"][der][param] = val
			else:
				# HVAC
				if der not in dat[adc]["HVAC"]:
					dat[adc]["HVAC"][der] = {}
				dat[adc]["HVAC"][der][param] = val

		if re.match('batt',der):
			# battery - store under inverter name
			inv = re.match('batt_(Binv_\S+)',der).group(1)
			if inv not in dat[adc]["BATT"]:
				dat[adc]["BATT"][inv] = {}
			param = "battery."+param
			dat[adc]["BATT"][inv][param] = val

		if re.match('Binv',der):
			# battery inverter
			if der not in dat[adc]["BATT"]:
				dat[adc]["BATT"][der] = {}
			param = "inverter."+param
			dat[adc]["BATT"][der][param] = val

		if re.match('solar',der):
			# solar array - store under inverter name
			inv = re.match('solar_(PVinv_\S+)',der).group(1)
			if inv not in dat[adc]["PV"]:
				dat[adc]["PV"][inv] = {}
			param = "solar."+param
			dat[adc]["PV"][inv][param] = val

		if re.match('PVinv',der):
			# PV inverter
			if der not in dat[adc]["PV"]:
				dat[adc]["PV"][der] = {}
			param = "inverter."+param
			dat[adc]["PV"][der][param] = val

#	# print the structure
#	for adc in dat:
#		print("ADC: "+adc)
#		for der_t in dat[adc]:
#			print("\t"+der_t+":")
#			for der in dat[adc][der_t]:
#				print("\t\t"+der)
#				for param in dat[adc][der_t][der]:
#					print("\t\t\t"+param+" -> "+str(dat[adc][der_t][der][param]))


	# ----------------------------------------------------------------------------
	# THIS IS WHERE THE ADC MANAGER SHOULD BE CALLED
	# ----------------------------------------------------------------------------
	# We need a module named ADC_Manager based on the existing demo
	#  - The module should have a subroutine called synch
	#  - Dat is the input to ADC_Manager.synch
	#  - A dictionary of similar structure needs to be returned

#	# This line is not necessary after ADC_Manager.synch is implemented
#	mgr_dat = {}

	# Uncomment this line once ADC_Manager.synch is implemented as described
	mgr_dat = ADC_Manager.synch(dat,timestamp=timestamp)


	# ----------------------------------------------------------------------------
	# ASSEMBLE KEY-VALUE PAIRS FROM MGR_DAT
	# ----------------------------------------------------------------------------
	pubkeys = []
	pubvals = []
	for adc in mgr_dat:
		for wh in mgr_dat[adc]["WH"]:
			for param in mgr_dat[adc]["WH"][wh]:
				pubkeys.append( adc + '_' + wh + '_' + param )
				pubvals.append( str( mgr_dat[adc]["WH"][wh][param] ) )
		for hvac in mgr_dat[adc]["HVAC"]:
			for param in mgr_dat[adc]["HVAC"][hvac]:
				pubkeys.append( adc + '_' + hvac + '_' + param )
				pubvals.append( str( mgr_dat[adc]["HVAC"][hvac][param] ) )
		for batt in mgr_dat[adc]["BATT"]:
			for param in mgr_dat[adc]["BATT"][batt]:
				m = re.match("(.+?)\.(.+)",param)
				if m:
					if m.group(1) == "inverter":
						der = batt
					elif m.group(1) == "battery":
						der = "batt_"+batt
					else:
						print("ERROR: unrecognized battery parameter "+param)
						print(m.group(1))
						print(m.group(2))
						return
					pubkeys.append( adc+ '_' + der + '_' + m.group(2) )
					pubvals.append( str( mgr_dat[adc]["BATT"][batt][param] ) )
				else:
					print("ERROR: unrecognized battery parameter "+param)
					return
		for pv in mgr_dat[adc]["PV"]:
			for param in mgr_dat[adc]["PV"][pv]:
				m = re.match("(.+?)\.(.+)",param)
				if m:
					if m.group(1) == "inverter":
						der = pv
					elif m.group(1) == "solar":
						der = "solar_"+pv
					else:
						print("ERROR: unrecognized pv parameter "+param)
						return
					pubkeys.append( adc + '_' + der + '_' + m.group(2) )
					pubvals.append( str( mgr_dat[adc]["PV"][pv][param] ) )
				else:
					print("ERROR: unrecognized pv parameter "+param)
					return

	return pubkeys , pubvals
