import re

# Scan the file for mpc.baseMVA and load setpoints
baseMVA = 0
loadPs = {}
loadQs = {}
ifh = open('../PFO/data/case24_ieee_rts.m','r');
line = ifh.readline()
while line is not '':
	# Check for baseMVA
	m = re.search(r'mpc.baseMVA\s*=\s*([-\.\d]+)',line)
	if m:
		baseMVA = m.group(1)
	# Check for load definitions
	m = re.search(r'mpc.bus\s*=\s*\[\s*(\S*)',line)
	if m:
		# Skip to the first load defnition
		if m.group(1):
			line = m.group(1)
		else:
			line = ifh.readline()
		# Begin load definitions
		in_busdefs = True
		while in_busdefs:
			# Make sure that this line is a valid load defnition
			m = re.search(r'\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*;',line)
			if m:
				loadPs[str(m.group(1))] = float(m.group(3))
				loadQs[str(m.group(1))] = float(m.group(4))
			else:
				print('Warning: unrecognized line\n\t'+line)
			line = ifh.readline()
			if re.search(r']',line) or line is '':
				in_busdefs = False
	if line is not '':
		line = ifh.readline()
ifh.close()

# print(baseMVA)
# print(loadPs)
# print(loadQs)

# Write the constraints file
delta = 0.2
ofh = open('data/case24_flex.csv','w')
# Write header
# Note: A*[p|q] <= b
ofh.write('load_name,A,b\n')
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
	
