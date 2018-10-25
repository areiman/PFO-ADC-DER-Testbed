def obj(parent,model,line,itr,oidh,octr):
	'''
	Store an object in the model structure
	Inputs:
		parent: name of parent object (used for nested object defs)
		model: dictionary model structure
		line: glm line containing the object definition
		itr: iterator over the list of lines
		oidh: hash of object id's to object names
		octr: object counter
	'''
	octr += 1
	# Identify the object type
	m = re.search('object ([^:{\s]+)[:{\s]',line,re.IGNORECASE)
	type = m.group(1)
	# If the object has an id number, store it
	n = re.search('object ([^:]+:[^{\s]+)',line,re.IGNORECASE)
	if n:
		oid = n.group(1)
	line = next(itr)
	# Collect parameters
	oend = 0
	oname = None
	params = {}
	if parent is not None:
		params['parent'] = parent
		# print('nested '+type)
	while not oend:
		m = re.match('\s*(\S+) ([^;{]+)[;{]',line)
		if m:
			# found a parameter
			param = m.group(1)
			val = m.group(2)
			intobj = 0
			if param == 'name':
				oname = val
			elif param == 'object':
				# found a nested object
				intobj += 1
				if oname is None:
					print('ERROR: nested object defined before parent name')
					quit()
				line,octr = obj(oname,model,line,itr,oidh,octr)
			elif re.match('object',val):
				# found an inline object
				intobj += 1
				line,octr = obj(None,model,line,itr,oidh,octr)
				params[param] = 'OBJECT_'+str(octr)
			else:
				params[param] = val
		if re.search('}',line):
			if intobj:
				intobj -= 1
				line = next(itr)
			else:
				oend = 1
		else:
			line = next(itr)
	# If undefined, use a default name
	if oname is None:
		oname = 'OBJECT_'+str(octr)
	oidh[oname] = oname
	# Hash an object identifier to the object name
	if n:
		oidh[oid] = oname
	# Add the object to the model
	if type not in model:
		# New object type
		model[type] = {}
	model[type][oname] = {}
	for param in params:
		model[type][oname][param] = params[param]
	# Return the 
	return line,octr

# ------------------
# Process each model
#-------------------
import re
import glob
import os
import math
import random
random.seed(0)

for ifn in glob.glob("IEEE-123-feeder/IEEE_123_feeder_0/IEEE_123_feeder_0.glm"):
	wd = os.getcwd()
	m = re.match(r'(.+).glm',ifn)
	if m:
		modelname = re.sub('[-\.]','_',m.group(1))
	else:
		modelname = 'default'
	n = re.search(r'(R\d-\d\d\.\d\d-\d).glm',ifn)
	if n:
		taxname = n.group(1)
	else:
		taxname = 'default'
	print("Processing "+taxname+"... "+ifn)
	inf = open(ifn,'r')

	#-----------------------
	# Pull Model Into Memory
	#-----------------------
	lines = []
	line = inf.readline()
	while line is not '':
		while re.match('\s*//',line) or re.match('\s+$',line):
			# skip comments and white space
			line = inf.readline()
		lines.append(line)
		line = inf.readline()
	inf.close()
	
	#--------------------------
	# Build the model structure
	#--------------------------
	octr = 0;
	model = {}
	h = {}		# OID hash
	clock = {}
	modules = {}
	classes = {}
	directives = []
	itr = iter(lines)
	for line in itr:
		# Look for objects
		if re.search('object',line):
			line,octr = obj(None,model,line,itr,h,octr)
		# Look for # directives
		if re.match('#\s?\w',line):
			directives.append(line)
		# Look for the clock
		m_clock = re.match('clock\s*([;{])',line,re.IGNORECASE)
		if (m_clock):
			# Clock found: look for parameters
			if m_clock.group(1) == '{':
				# multi-line clock definition
				oend = 0
				while not oend:
					line = next(itr)
					m_param = re.search('(\w+)\s+([^;\n]+)',line)
					if m_param:
						# Parameter found
						clock[m_param.group(1)]=m_param.group(2)
					if re.search('}',line):
						# End of the clock definition
						oend = 1
		# Look for module defintions
		m_mtype = re.search('module\s+(\w+)\s*([;{])',line,re.IGNORECASE)
		if (m_mtype):
			# Module found: look for parameters
			modules[m_mtype.group(1)] = {}
			if m_mtype.group(2) == '{':
				# multi-line module definition
				oend = 0
				while not oend:
					line = next(itr)
					m_param = re.search('(\w+)\s+([^;\n]+)',line)
					if m_param:
						# Parameter found
						modules[m_mtype.group(1)][m_param.group(1)] =\
								m_param.group(2)
					if re.search('}',line):
						# End of the module
						oend = 1
		# Look for class definitions
		m_ctype = re.search('class\W+(\w+)\s*([;{])',line,re.IGNORECASE)
		if (m_ctype):
			# Class found: look for parameters
			classes[m_ctype.group(1)] = {}
			if m_ctype.group(2) == '{':
				# multi-line class definition
				oend = 0
				while not oend:
					line = next(itr)
					m_param = re.search('(\w+)\s+([^;\n]+)',line)
					if m_param:
						# Parameter found
						classes[m_ctype.group(1)][m_param.group(1)] =\
								m_param.group(2)
					if re.search('}',line):
						# End of the class
						oend = 1
	
	#------------------------------
	# Update all object name values
	#------------------------------
	for t in model:
		for o in model[t]:
			for p in model[t][o]:
				if model[t][o][p] in h:
					model[t][o][p] = h[model[t][o][p]]
	
	
	# Print the oid hash
	# print('oidh:')
	# for x in h:
		# print(x+'->'+h[x])
	# print('end oidh')
	
	# Print the model structure
	# for t in model:
		# print(t+':')
		# for o in model[t]:
			# print('\t'+o+':')
			# for p in model[t][o]:
				# if ':' in model[t][o][p]:
					# print('\t\t'+p+'\t-->\t'+h[model[t][o][p]])
				# else:
					# print('\t\t'+p+'\t-->\t'+model[t][o][p])
					
	
	
	#--------------------
	# Add new DER
	#--------------------
	# Add PV Systems
	modules['generators'] = {}
	if 'inverter' not in model:
		model['inverter'] = {}
	if 'solar' not in model:
		model['solar'] = {}
	if 'battery' not in model:
		model['battery'] = {}
	# Reseed random for PV deployment
	random.seed(0)
	for house in model['house']:
		if random.random() <= 0.168:
			# rolled positive for PV
			# nominal size is nominal house load times %PVload/%PVcust
			# note that %PVload is percentage of peak load
			pvsizeNom = 3000*24.97/16.8
			pvsize = random.gauss(pvsizeNom,math.sqrt(pvsizeNom/3))
			PVinvname = 'PVinv_'+house
			solarname = 'solar_'+PVinvname
			# The inverter is actually attached to the triplex meter
			parent = model['house'][house]['parent']
			phases = model['triplex_meter'][parent]['phases']
			# Set up the inverter
			model['inverter'][PVinvname] = {}
			model['inverter'][PVinvname]['parent'] = parent
			model['inverter'][PVinvname]['groupid'] = 'PV_inverter'
			model['inverter'][PVinvname]['phases'] = phases
			model['inverter'][PVinvname]['generator_mode'] = 'SUPPLY_DRIVEN'
			model['inverter'][PVinvname]['generator_status'] = 'ONLINE'
			model['inverter'][PVinvname]['inverter_type'] = 'FOUR_QUADRANT'
			model['inverter'][PVinvname]['four_quadrant_control_mode'] = 'CONSTANT_PF'
			model['inverter'][PVinvname]['power_factor'] = str(1.0)
			model['inverter'][PVinvname]['inverter_efficiency'] = str(1.0)
			model['inverter'][PVinvname]['rated_power'] = str(pvsize)
			# Set up the solar PV array
			model['solar'][solarname] = {}
			model['solar'][solarname]['parent'] = PVinvname
			model['solar'][solarname]['generator_mode'] = 'SUPPLY_DRIVEN'
			model['solar'][solarname]['generator_status'] = 'ONLINE'
			model['solar'][solarname]['rated_power'] = str(pvsize)
			model['solar'][solarname]['panel_type'] = 'SINGLE_CRYSTAL_SILICON'
	# Reseed random for battery deployment
	random.seed(0)
	for house in model['house']:
		if random.random() <= 0.515:
			# rolled positive for battery (BEV)
			# nominal size is nominal house load times %BEVload/%BEVcust
			# note that %BEVload is percentage of peak load
			battSNom = 3000*17.97/51.5	# This could be a normal distribution
			battS = random.gauss(battSNom,math.sqrt(battSNom/3))
			battENom = 30
			battE = random.gauss(battENom,math.sqrt(battENom/3))
			Binvname = 'Binv_'+house
			battname = 'batt_'+Binvname
			# The inverter is actually attached to the triplex meter
			parent = model['house'][house]['parent']
			phases = model['triplex_meter'][parent]['phases']
			# Set up the inverter
			model['inverter'][Binvname] = {}
			model['inverter'][Binvname]['parent'] = parent
			model['inverter'][Binvname]['groupid'] = 'battery_inverter'
			model['inverter'][Binvname]['phases'] = phases
			model['inverter'][Binvname]['generator_mode'] = 'CONSTANT_PQ'
			model['inverter'][Binvname]['generator_status'] = 'ONLINE'
			model['inverter'][Binvname]['inverter_type'] = 'FOUR_QUADRANT'
			model['inverter'][Binvname]['four_quadrant_control_mode'] = 'CONSTANT_PQ'
			model['inverter'][Binvname]['inverter_efficiency'] = str(1.0)
			model['inverter'][Binvname]['rated_power'] = str(battS)
			model['inverter'][Binvname]['P_Out'] = str(0.0)
			model['inverter'][Binvname]['Q_Out'] = str(0.0)
			# Set up the battery
			model['battery'][battname] = {}
			model['battery'][battname]['parent'] = Binvname
			model['battery'][battname]['use_internal_battery_model'] = 'true'
			model['battery'][battname]['generator_mode'] = 'SUPPLY_DRIVEN'
			model['battery'][battname]['generator_status'] = 'ONLINE'
			model['battery'][battname]['battery_capacity'] = str(battE)
			model['battery'][battname]['rated_power'] = str(battS)
			model['battery'][battname]['round_trip_efficiency'] = str(1.0)
			model['battery'][battname]['state_of_charge'] = str(0.5)
			model['battery'][battname]['nominal_voltage'] = str(260)
			model['battery'][battname]['battery_type'] = 'LI_ION'
	
	
	#--------------------------------------------------------
	# Add group recorders for DER characterization parameters
	#--------------------------------------------------------
	if 'group_recorder' not in model:
		model['group_recorder'] = {}
	# Waterheater characterization parameters
	for property in [\
			'heat_mode',\
			'tank_volume',\
			'tank_height',\
			'heating_element_capacity',\
			'thermostat_deadband']:
		rec_name = 'recorder_wh_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"class=waterheater"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	# HVAC characterization parameters
	for property in [\
			'air_heat_capacity',\
			'mass_heat_capacity',\
			'mass_heat_coeff',\
			'UA',\
			'heating_system_type',\
			'cooling_system_type',\
			'auxiliary_system_type',\
			'design_heating_capacity',\
			'design_cooling_capacity',\
			'auxiliary_heat_capacity',\
			'thermostat_deadband']:
		rec_name = 'recorder_hvac_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"groupid=Residential"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	# Battery characterization parameters
	for property in [\
			'rated_power',\
			'battery_capacity']:
		rec_name = 'recorder_batt_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"class=battery"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	# Battery inverter characterization parameters
	for property in [\
			'rated_power',\
			'inverter_efficiency',\
			'max_charge_rate',\
			'max_discharge_rate']:
		rec_name = 'recorder_battInv_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"groupid=battery_inverter"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	# Solar PV characterization parameters
	for property in [\
			'rated_power']:
		rec_name = 'recorder_solar_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"class=solar"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	# Solar PV inverter characterization parameters
	for property in [\
			'inverter_efficiency']:
		rec_name = 'recorder_solarInv_'+property
		model['group_recorder'][rec_name] = {}
		model['group_recorder'][rec_name]['group'] = '"groupid=PV_inverter"'
		model['group_recorder'][rec_name]['property'] = property
		model['group_recorder'][rec_name]['interval'] = str(3600)
		model['group_recorder'][rec_name]['limit'] = str(1)
		model['group_recorder'][rec_name]['file'] = rec_name+'.csv'
	
	#-------------------
	# Develop Bus Tree
	#-------------------
	
	# Build lists of relevant objects
	swingbus = ''
	# linklist = []
	links = {}
	# nodelist = []
	nodes = {}
	for t in ['substation','house','node','meter','triplex_node','triplex_meter','load']:
		if t in model:
			for o in model[t]:
				if 'bustype' in model[t][o]:
					if model[t][o]['bustype'] == 'SWING':
						swingbus = o
				# nodelist.append(o)
				nodes[o] = model[t][o]
	for t in ['fuse','transformer','switch','triplex_line'\
			,'underground_line','overhead_line','recloser','regulator']:
		if t in model:
			for o in model[t]:
				# linklist.append(o)
				links[o] = model[t][o]
	
	# Hash nodes to their parents
	h = {}
	for node in nodes:
		if 'parent' in nodes[node].keys():
			h[node] = nodes[node]['parent']
		else:
			h[node] = node
	
	# Rehash nodes to the their oldest ancestor
	for node in h:
		# print(node)
		tmp = node
		while tmp != h[tmp]:
			tmp = h[tmp]
		h[node] = tmp
	
	# Hash ancesteral nodes to a position and positions back to names
	names = []
	i = {}
	ctr = 0
	for node in set(h.values()):
		ctr += 1
		i[node] = ctr
		names.append(node)
		
	# Test that ancesteral nodes are hashed to a unique position
	# print(ctr)
	# tmp = []
	# for a in i.values():
		# tmp.append(a)
	# print(sorted(tmp))
	# c = 0
	# for a in sorted(tmp):
		# c += 1
		# if a != c:
			# print('BAD')
	# print('HI')
	
	# Build the tree vector: tree[position] = upstream_positon
	tree = [0]*ctr
	# set the swing bus as a root
	tree[i[h[swingbus]]] = 0;
	for link in links:
		fromnode = links[link]['from']
		m = re.search(r':(\d+)',fromnode)
		if m:
			fromnode = m.group(1)
		# print(fromnode)
		
		tonode = links[link]['to']
		m = re.search(r':(\d+)',tonode)
		if m:
			tonode = m.group(1)
		# print(tonode)
		
		tree[i[h[tonode]]-1] = i[h[fromnode]]
	
	tmpf = open('_tree.csv','w')
	for a in tree:
		tmpf.write(str(a)+'\n')
	# print(t)
	tmpf.close()
	
	
	#---------------------------
	# Load the ADC Location List
	#---------------------------
	adchash = {}
	adcs = {}
	# The following list is based on initial voltage analysis
	# A non-behavorial version of the model was used
	# A voltage drop up to the aggregate load locations of 0.02 was permitted
	inf = open('C:/Users/reim112/Documents/PNNL/GMLC_Control/ADC_Location/ADC_Placement_by_Voltage_Drop.csv')
	line = inf.readline()		# skip the headder
	while line is not '':
		# line = inf.readline()
		m = re.search(r'([^,\s]*),[^,\s]*,[^,\s]*,[^,\s]*,[^,\s]*,[^,\s]*,([^,\s]*)',line)
		if m:
			# print(m.group(1)+' -> '+m.group(2))
			adchash[m.group(1)] = m.group(2)
			adcs[m.group(2)] = {}
		line = inf.readline()
	
	DER_TYPES = ['Waterheaters','HVACs','Photovoltaics','Batteries']
	for adc in adcs:
		for dertype in DER_TYPES:
			adcs[adc][dertype] = {}
	
	#-----------------------
	# Associate DER with ADC
	#-----------------------
	# Waterheaters
	for wh in model['waterheater']:
		# Trace up to a recognized node
		upidx = tree[i[h[model['waterheater'][wh]['parent']]]-1]
		while upidx:
			nodename = names[upidx-1]
			candidate = re.sub(r'[nl]',r'',nodename)
			if candidate in adchash.keys():
				adcs[adchash[candidate]]['Waterheaters'][wh] = {}
				# adcs[adchash[candidate]]['Waterheaters'][wh]['tank_volume'] =\
					# model['waterheater'][wh]['tank_volume']
				# adcs[adchash[candidate]]['Waterheaters'][wh]['tank_height'] =\
					# model['waterheater'][wh]['tank_height']
				# adcs[adchash[candidate]]['Waterheaters'][wh]['heating_element_capacity'] =\
					# model['waterheater'][wh]['heating_element_capacity']
				# adcs[adchash[candidate]]['Waterheaters'][wh]['thermostat_deadband'] =\
					# model['waterheater'][wh]['thermostat_deadband']
				upidx = 0
			else:
				upidx = tree[upidx-1]
	# Electric ACs
	for house in model['house']:
		if model['house'][house]['cooling_system_type'] == 'ELECTRIC':
			# Trace up to a recognized node
			upidx = tree[i[h[house]]-1]
			while upidx:
				nodename = names[upidx-1]
				candidate = re.sub(r'[nl]',r'',nodename)
				if candidate in adchash.keys():
					adcs[adchash[candidate]]['HVACs'][house] = {}
					upidx = 0
				else:
					upidx = tree[upidx-1]
	# Solar PV systems
	for pv in model['solar']:
		# Trace up to a recognized node -- start at the parent inverter's parent
		upidx = tree[i[h[model['inverter'][model['solar'][pv]['parent']]['parent']]]-1]
		while upidx:
			nodename = names[upidx-1]
			candidate = re.sub(r'[nl]',r'',nodename)
			if candidate in adchash.keys():
				adcs[adchash[candidate]]['Photovoltaics'][pv] = {}
				# adcs[adchash[candidate]]['Photovoltaics'][pv]['rated_power'] =\
					# model['solar'][pv]['rated_power']
				adcs[adchash[candidate]]['Photovoltaics'][pv]['inverter'] =\
					model['solar'][pv]['parent']
				# adcs[adchash[candidate]]['Photovoltaics'][pv]['inverter.inverter_efficiency'] =\
					# model['inverter'][model['solar'][pv]['parent']]['inverter_efficiency']
				upidx = 0
			else:
				upidx = tree[upidx-1]
	# Battery systems
	for batt in model['battery']:
		# Trace up to a recognized node -- start at the parent inverter's parent
		upidx = tree[i[h[model['inverter'][model['battery'][batt]['parent']]['parent']]]-1]
		while upidx:
			nodename = names[upidx-1]
			candidate = re.sub(r'[nl]',r'',nodename)
			if candidate in adchash.keys():
				adcs[adchash[candidate]]['Batteries'][batt] = {}
				# adcs[adchash[candidate]]['Batteries'][batt]['rated_power'] =\
					# model['battery'][batt]['rated_power']
				# adcs[adchash[candidate]]['Batteries'][batt]['battery_capacity'] =\
					# model['battery'][batt]['battery_capacity']
				adcs[adchash[candidate]]['Batteries'][batt]['inverter'] =\
					model['battery'][batt]['parent']
				# adcs[adchash[candidate]]['Batteries'][batt]['inverter.inverter_efficiency'] =\
					# model['inverter'][model['battery'][batt]['parent']]['inverter_efficiency']
				upidx = 0
			else:
				upidx = tree[upidx-1]
	
	
	
	#----------------
	# Print DER Files
	#----------------
	# Summary File
	outf = open('DER/DER_Summary.csv','w')
	outf.write('ADC')
	for dertype in DER_TYPES:
		outf.write(','+dertype)
	outf.write(',total\n')
	for adc in adcs:
		ctr = 0
		ctrs = {}
		outf.write(adc)
		for dertype in DER_TYPES:
			ctrs[dertype] = 0
			for der in adcs[adc][dertype]:
				ctrs[dertype] += 1
				ctr += 1
			outf.write(','+str(ctrs[dertype]))
		outf.write(','+str(ctr)+'\n')
	outf.close();
	
	# DER Lists
	for adc in adcs:
		adcname = 'ADC_'+adc
		if wd+'\\DER\\'+adcname not in glob.glob(wd+'\\DER\\*'):
			os.system('mkdir '+wd+'\\DER\\'+adcname)
			print(glob.glob(wd+'\\DER\\'))
		for dertype in adcs[adc]:
			outf = open('DER/'+adcname+'/'+adcname+'_'+dertype+'.txt','w')
			for der in adcs[adc][dertype]:
				outf.write(der)
				for param in adcs[adc][dertype][der]:
					outf.write(','+param+'='+adcs[adc][dertype][der][param])
				outf.write('\n')
			outf.close()
	
	
	#------------------
	# Rewrite the Model
	#------------------
	# Establish the the file name
	m_fn = re.search('([^.]+).glm',ifn,re.IGNORECASE)
	if m_fn:
		ofn = m_fn.group(1)+'_DER'+'.glm'
	else:
		print('Error: Unable to construct output filename')
	
	# Open the output file
	outf = open(ofn,'w')
	
	# Write the clock
	outf.write('clock')
	if len(clock) == 0:
		outf.write('\n')
	else:
		outf.write(' {\n')
		for param in clock:
			outf.write('\t'+param+' '+clock[param]+';\n')
		outf.write('}\n')
	outf.write('\n')
		
	# Write the '#' directives
	for directive in directives:
		outf.write(directive)
	outf.write('\n')
	
	# Write the moduls
	for module in modules:
		outf.write('module '+module)
		if len(modules[module]) == 0:
			outf.write(';\n')
		else:
			outf.write(' {\n')
			for param in modules[module]:
				outf.write('\t'+param+' '+modules[module][param]+';\n')
			outf.write('};\n')
		outf.write('\n')
	
	# Write the classes
	for c in classes:
		outf.write('class '+c)
		if len(classes[c]) == 0:
			outf.write(';\n')
		else:
			outf.write(' {\n')
			for param in classes[c]:
				outf.write('\t'+param+' '+classes[c][param]+';\n')
			outf.write('};\n')
		outf.write('\n')
		
	# Write the objects
	objctr = 0
	for t in model:
		for o in model[t]:
			objctr += 1
			# write each object
			outf.write('object '+t+' {\n')
			outf.write('\tname '+o+';\n')
			for p in model[t][o]:
				outf.write('\t'+p+' '+model[t][o][p]+';\n')
			outf.write('}\n\n')
	print('\tTotal objects written: '+str(objctr))
	
	# Print PV debugging recorders
	# outf.write('object group_recorder {\n')
	# outf.write('	name tmp_recorder;\n')
	# outf.write('	group "groupid=Residential_Meter";\n')
	# outf.write('	property measured_real_power;\n')
	# outf.write('	file "res_meters.csv";\n')
	# outf.write('	interval 15;\n')
	# outf.write('	limit 5760;\n')
	# outf.write('}\n')
	# outf.write('\n')
	# outf.write('object recorder {\n')
	# outf.write('	name my_solar_recorder;\n')
	# outf.write('	parent solar_PVinv_house3_l4_tm;\n')
	# outf.write('	property Insolation,VA_Out;\n')
	# outf.write('	file solar_meter.csv;\n')
	# outf.write('	interval 15;\n')
	# outf.write('	limit 5760;\n')
	# outf.write('}\n')
