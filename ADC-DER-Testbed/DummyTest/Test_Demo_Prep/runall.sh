#!/bin/bash 
 
clear 
 
cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo_Prep/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_TRACE=yes && export FNCS_BROKER=tcp://*:5570 && exec fncs_broker 2 &> broker.log &

cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo_Prep/GLD/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_BROKER=tcp://localhost:5570 && exec gridlabd IEEE_123_feeder_0_DER_demo-recorders_Rev0.glm &> glm.log &

cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo_Prep/Python/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_BROKER=tcp://localhost:5570 && FNCS_CONFIG_FILE=fncs.zpl && exec python3.6 FNCS_API.py 10 FNCS_API.txt &> FNCS_API.out &

wait 
 
exit 0 
