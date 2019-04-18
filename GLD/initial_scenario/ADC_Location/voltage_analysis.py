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
for ifn in glob.glob("*.glm"):
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
					
					
	#-------------------
	# Develop Bus Tree
	#-------------------
	
	# Build lists of relevant objects
	swingbus = ''
	# linklist = []
	links = {}
	# nodelist = []
	nodes = {}
	for t in ['house','node','meter','triplex_node','triplex_meter','load']:
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
	
	#---------------------
	# Load Voltage Profile
	#---------------------
	vprofile = {}
	voltf = open('voltages.csv','r')
	# Skip to header lines
	line = voltf.readline()
	line = voltf.readline()
	line = voltf.readline()
	while line is not '':
		# print(line)
		toks = re.split(r'[,\s]',line)
		# print(toks)
		if toks[0] == '610':
			vbase = 277.128
		else:
			vbase = 2401.7771
		reVa = float(toks[1])/vbase
		imVa = float(toks[2])/vbase
		reVb = float(toks[3])/vbase
		imVb = float(toks[4])/vbase
		reVc = float(toks[5])/vbase
		imVc = float(toks[6])/vbase
		Va = math.sqrt( reVa*reVa + imVa*imVa )
		Vb = math.sqrt( reVb*reVb + imVb*imVb )
		Vc = math.sqrt( reVc*reVc + imVc*imVc )
		voltages = []
		if Va:
			voltages.append(Va)
		if Vb:
			voltages.append(Vb)
		if Vc:
			voltages.append(Vc)
		vprofile[toks[0]] = min(voltages)
		line = voltf.readline()
	inf.close()
	
	nodeints = []
	for node in vprofile.keys():
		nodeints.append(int(node))
	for node in sorted(nodeints):
		print('Bus '+str(node)+' voltage: '+str(vprofile[str(node)])+' p.u.')
		
	# ----------------------------------
	# Determine voltage drop below nodes
	# ----------------------------------
	
	# initialize data structures
	vminbelow = [0]*ctr
	for node in nodes:
		vminbelow[i[h[node]]-1] = vprofile[node]
	dropbelow = [0]*ctr
	loadsbelow = [0]*ctr
	
	# count loads
	for t in ['load','triplex_load']:
		if t in model:
			for load in model[t]:
				# count the load for itself
				loadsbelow[i[h[load]]-1] += 1
				# move up
				upidx = i[h[load]]
				while upidx:
					loadsbelow[upidx-1] += 1
					upidx = tree[upidx-1]
	
	# trace up vminbelow
	for node in nodes:
		upidx = tree[i[h[node]]-1]
		while upidx:
			if vminbelow[upidx-1] > vminbelow[i[h[node]]-1]:
				vminbelow[upidx-1] = vminbelow[i[h[node]]-1]
				upidx = tree[upidx-1]
			else:
				upidx = 0
	
	# compute drop below
	for node in nodes:
		dropbelow[i[h[node]]-1] = vprofile[node] - vminbelow[i[h[node]]-1]
	
	dvthresh = 0.02
	adcbuss = ['err']*ctr
	# Determine ADC Buses
	for node in nodes:
		# start here
		adcbus = 'NONE'
		upidx = i[h[node]]
		while dropbelow[upidx-1] < dvthresh:
			adcbus = names[upidx-1]
			upidx = tree[upidx-1]
		adcbuss[i[h[node]]-1] = adcbus
	
	# Print output
	for node in sorted(nodeints):
		print('Bus '+str(node)+' - '+'vminphase: '+str(vprofile[str(node)]) +\
				'; upstream bus: '+names[tree[i[h[str(node)]]-1]-1] +\
				'; loads below: '+str(loadsbelow[i[h[str(node)]]-1]) +\
				'; min v below: '+str(vminbelow[i[h[str(node)]]-1]) +\
				'; vdrop below: '+str(dropbelow[i[h[str(node)]]-1]) +\
				'')
	
	# write output to file
	outf = open('ADC_Placement_by_Voltage_Drop.csv','w')
	outf.write('Bus Name,'+\
			'Vmag min phase,'+\
			'min Vmag phase below,'+\
			'Vdrop below,'+\
			'loads below,'+\
			'Upstream Bus,'+\
			'ADC Bus ('+str(dvthresh)+')\n')
	for node in sorted(nodeints):
		outf.write(str(node)+\
				','+str(vprofile[str(node)])+\
				','+str(vminbelow[i[h[str(node)]]-1])+\
				','+str(dropbelow[i[h[str(node)]]-1])+\
				','+str(loadsbelow[i[h[str(node)]]-1])+\
				','+names[tree[i[h[str(node)]]-1]-1]+\
				','+str(adcbuss[i[h[str(node)]]-1])+\
				'\n')
				
	