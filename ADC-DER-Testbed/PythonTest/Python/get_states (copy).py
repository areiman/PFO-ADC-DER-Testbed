import string;
import sys;
import fncs;
import matlab.engine


eng = matlab.engine.start_matlab()
time_stop = int(sys.argv[1])
time_granted = 0
op = open (sys.argv[2], "w")

# requires the yaml file
fncs.initialize()
print("# time      key       value", file=op)

while time_granted < time_stop:
    time_granted = fncs.time_request(time_stop)
    events = fncs.get_events()
    for key in events:
        print(time_granted, key.decode(), fncs.get_value(key).decode(), file=op)
    #[topic, values] = eng.DummyADC()
    #for i in values:
    #    fncs.publish(str(topic[i]), values[i])	    
    #fncs.publish(str(topic), power_changed)
     
    #volt=matlab.double(voltage)  
    #real_power=matlab.double(power_kW) 
    #eng.plot(volt)
    #eng.plot(real_power)
    #print(voltage,power_kW, file=op)

fncs.finalize()
op.close()
