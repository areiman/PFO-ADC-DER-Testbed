import re
import math

# Scan the file for mpc.baseMVA and load setpoints
baseMVA = 0
loadPs = {}
loadQs = {}
ifh = open('refs/IEEE123Loads.DSS','r');
line = ifh.readline()
while line is not '':
	# Check for baseMVA
	m = re.search(r'new\s+load\.(\S+)',line,re.IGNORECASE)
	if m:
		loadname = m.group(1)
		# print(loadname)
		
		# load definition line
		P = 0
		mp = re.search(r'kw\s*=\s*(\S+)',line,re.IGNORECASE)
		if mp:
			P = float(mp.group(1))
		else:
			print('Warning: undetermined P for '+loadname+'\n')
		Q = 0
		mq = re.search(r'kvar\s*=\s*(\S+)',line,re.IGNORECASE)
		if mq:
			Q = float(mq.group(1))
		else:
			print('Warning: undetermined Qfor '+loadname+'\n')
		# Note: there are other ways of specifying P and Q; this is used in this file
		
		# Determine bus and phases
		bus = ''
		phs = []
		mbus = re.search(r'bus1\s*=\s*(\S+)',line,re.IGNORECASE)
		if mbus:
			tmp = mbus.group(1)
			toks = re.split(r'\.',tmp)
			bus = toks[0]
			phs = toks[1:]
		# print(bus)
		# print(phs)
		
		# Determine connection
		conn = ''
		mconn = re.search(r'conn\s*=\s*(\S+)',line,re.IGNORECASE)
		if mconn:
			conn = mconn.group(1)
		else:
			print('Warning: undetermined connection for '+loadname+'\n')
		# print('\t'+conn)
		
		# Determine number of phases
		nphs = 0
		mnphs = re.search(r'phases\s*=\s*(\S+)',line,re.IGNORECASE)
		if mnphs:
			nphs = float(mnphs.group(1))
		else:
			print('Warning: undetermined number of phases for '+loadname+'\n')
		# print('\t'+str(nphs))
		
		# Handle P and Q according to connection and number of phases
		if re.match(conn,'wye',re.IGNORECASE):
			if nphs == 1 or nphs == 2:
				if len(phs) == 0:
					print('Warning: phasing indeterminate for '+loadname)
				elif len(phs) != nphs:
					print('Warning: phase/node mismatch for '+loadname)
				for ph in phs:
					node = bus+'.'+ph
					loadPs[node] = P/nphs
					loadQs[node] = Q/nphs
			elif nphs == 3:
				if len(phs) == 0:
					phs = ['1','2','3']
				if len(phs) != 3:
					print('Warning: phase/node mismatch for '+loadname)
				for ph in phs:
					node = bus+'.'+ph
					loadPs[node] = P/nphs
					loadQs[node] = Q/nphs
			else:
				print('Warning: unrecognized number of phases')
		elif re.match(conn,'delta',re.IGNORECASE):
			# Define the nominal voltage for each phase
			vnom = [0,\
				math.cos(+000*math.pi/180)+1j*math.sin(+000*math.pi/180),\
				math.cos(-120*math.pi/180)+1j*math.sin(-120*math.pi/180),\
				math.cos(+120*math.pi/180)+1j*math.sin(+120*math.pi/180)]
			if nphs == 1:
				if len(phs) != 2:
					print('Warning: phase/node mismatch for '+loadname)
				# Set up the complex power
				Sll = P + 1j*Q
				# These are the unit-indexed phases
				phinj = int(phs[0])
				phout = int(phs[1])
				# Refer the load power to the local Vln
				Sinj = Sll * vnom[phinj]/(vnom[phinj]-vnom[phout])
				Sout = Sll * vnom[phout]/(vnom[phout]-vnom[phinj])
				# Store P and Q for each node
				loadPs[bus+'.'+phs[0]] = Sinj.real
				loadQs[bus+'.'+phs[0]] = Sinj.imag
				loadPs[bus+'.'+phs[1]] = Sout.real
				loadQs[bus+'.'+phs[1]] = Sout.imag
			elif nphs == 2:
				if len(phs) != 3:
					print('Warning: phasing indeterminate for '+loadname)
				# Set up the complex power
				Sll = P + 1j*Q
				# These are the unit-indexed phases
				phinj = int(phs[0])
				phint = int(phs[1])
				phout = int(phs[2])
				# Refer the load power to the local Vln
				Sinj = Sll * vnom[phinj]/(vnom[phinj]-vnom[phint])
				Sint = Sll * \
					( vnom[phint]/(vnom[phint]-vnom[phinj]) +\
					  vnom[phint]/(vnom[phint]-vnom[phout]) )
				Sout = Sll * vnom[phout]/(vnom[phout]-vnom[phint])
				# Store P and Q for each node
				loadPs[bus+'.'+phs[0]] = Sinj.real
				loadQs[bus+'.'+phs[0]] = Sinj.imag
				loadPs[bus+'.'+phs[1]] = Sint.real
				loadQs[bus+'.'+phs[1]] = Sint.imag
				loadPs[bus+'.'+phs[2]] = Sout.real
				loadQs[bus+'.'+phs[2]] = Sout.imag
			elif nphs == 3:
				if len(phs) == 0:
					phs = ['1','2','3']
				if len(phs) != 3:
					print('Warning: phase/node mismatch for '+loadname)
				for ph in phs:
					node = bus+'.'+ph
					loadPs[node] = P/nphs
					loadQs[node] = Q/nphs
			else:
				print('Warning: unrecognized number of phases')
		else:
			print('Warning: unrecognized connection type \''+conn+'\'')
		# Move to the next line
		line = ifh.readline()
ifh.close()

# print(baseMVA)
# print(loadPs)
# print(loadQs)

# Write the constraints file
delta = 0.03
ofh = open('data/ieee123_flex.csv','w')
# Write header
# Note: A*[p|q] <= b
ofh.write('node_name,A,b\n')
for load in loadPs.keys():
	# write load name
	ofh.write(load)
	# write A
	ofh.write(',[1 0|-1 0|0 1|0 -1]')
	# write B
	ofh.write(',['+\
		str(loadPs[load]*+1*(1+delta))+'|'+\
		str(loadPs[load]*-1*(1-delta))+'|'+\
		str(loadQs[load]*+1*(1+delta))+'|'+\
		str(loadQs[load]*-1*(1-delta))+']')
	ofh.write('\n')
	
