import re

import fncs_parser

keys = []
vals = []

# Read the test output file fo build key and value lists
fh = open("get_states_old.txt",'r')
for line in fh:
	line = line.rstrip()
	m = re.search(r'/(\S+)\s+(.+)',line,re.IGNORECASE)
	if m:
		key = m.group(1)
		val = m.group(2)
		if re.match('1\s',line):
#			print(key+" -> "+val)
			keys.append(key)
			vals.append(val)

keys_from_adc_mgr,vals_from_adc_mgr = fncs_parser.synch(keys,vals)
print(keys_from_adc_mgr)
print(vals_from_adc_mgr)
