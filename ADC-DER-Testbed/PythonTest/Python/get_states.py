import string;
import sys;
import fncs;
import matlab.engine


eng = matlab.engine.start_matlab()
time_stop = int(sys.argv[1])
time_granted = 0
op = open (sys.argv[2], "a")


# requires the yaml file
fncs.initialize()
print("# time      key       value", file=op)

while time_granted < time_stop:
    time_granted = fncs.time_request(time_stop)
    events = fncs.get_events()
    SubKeys = []
    SubKeyVals = []
    for key in events:
        print(time_granted, key.decode(), fncs.get_value(key).decode(), file=op)
    #for key in range( len(events) ):
        Temp = str( key.decode()  ) + "   " + str( fncs.get_value(key).decode() )
        SubKeys.append( Temp ) 
        #Temp2 = str( fncs.get_value(key).decode() )
	#SubKeyVals.append( Temp2 )
    #SubKey = matlab.char(SubKeys)
    #SubKeyVal = matlab.char( SubKeysVals )
    #eng.eval('[keys, KeyVal] = DummyMAT( SubKey , SubKeyVal );',nargout=0)
    #key_val = eng.workspace['KeyVal']
    #keys = eng.workspace['keys']
    #print(key_val[0][121])
    #print(keys[121])
    a = eng.DummyMAT(SubKeys, nargout=2)
    key_val = a[1][0]
    keys = a[0]
    print("This is returned string from matlab about string", a[0])
    print("This is returned values from matlab about string", a[1][0])
    
    for i in range(len(keys)):
        fncs.publish(str(keys[i]), key_val[i])	    
    #fncs.publish(str(topic), power_changed)
     
    #volt=matlab.double(voltage)  
    #real_power=matlab.double(power_kW) 
    #eng.plot(volt)
    #eng.plot(real_power)
    #print(voltage,power_kW, file=op)

fncs.finalize()
op.close()
