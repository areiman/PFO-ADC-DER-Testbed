'''
This will be the production Co-Simulation Manager
'''

import re
import time
import fncs_parser
import sys
import fncs
import json

time_stop = int(sys.argv[1])
time_granted = 0
time_last = 0
control_timestep = 4
time_next = control_timestep
op = open (sys.argv[2], "w")
PQ_opt_dict={} #to store optimal PQ data from control modules

# requires the zpl/yaml file
fncs.initialize()
print('*****FNCS HAS INITIALIZED******')
print("# time      key       value", file=op)

print("**time stop = ", time_stop)
while time_granted < time_stop:
    # time_last = time_granted
    time_granted = fncs.time_request(time_next)
    # time_delta = time_granted - time_last
    print ("**time granted =  ", time_granted)
    print("**time next =  ", time_next)
    if time_granted == time_next and time_granted < time_stop:
        time_next = time_next + control_timestep
        events = fncs.get_events()
        SubKeys = []
        SubKeyVals = []
        for key in events:
            print(time_granted, key.decode(), fncs.get_value(key).decode(), file=op)
            Temp = str( key.decode())
            SubKeys.append(Temp)
            Temp=str( fncs.get_value(key).decode() )
            SubKeyVals.append(Temp)
        print("****SubKeys*****")
        print(SubKeys)
        keys,key_val = fncs_parser.synch(SubKeys,SubKeyVals, timestamp=time_granted)
        for i in range(len(keys)):
            # print(str(keys[i]))
            # print(str(key_val[i]))
          fncs.publish(str(keys[i]), str(key_val[i]))
		# time.sleep(5)

fncs.finalize()
op.close()
print('*****FNCS HAS ENDED******')