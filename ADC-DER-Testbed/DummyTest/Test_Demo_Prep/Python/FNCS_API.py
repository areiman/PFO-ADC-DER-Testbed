import string
import re
import time
import fncs_parser
import sys
import fncs
import matlab.engine

eng = matlab.engine.start_matlab()
time_stop = int(sys.argv[1])
time_granted = 0
op = open (sys.argv[2], "w")


# requires the zpl/yaml file
fncs.initialize()
print("# time      key       value", file=op)

while time_granted < time_stop:
	time_granted = fncs.time_request(time_stop)
	events = fncs.get_events()
	SubKeys = []
	SubKeyVals = []
	for key in events:
		print(time_granted, key.decode(), fncs.get_value(key).decode(), file=op)
		Temp = str( key.decode())
		SubKeys.append(Temp)
		Temp=str( fncs.get_value(key).decode() )
		SubKeyVals.append(Temp)
	keys,key_val = fncs_parser.synch(SubKeys,SubKeyVals)

	for i in range(len(keys)):
		print(str(keys[i]))
		print(str(key_val[i]))
		fncs.publish(str(keys[i]), str(key_val[i]))   
	time.sleep(5)

fncs.finalize()
op.close()
