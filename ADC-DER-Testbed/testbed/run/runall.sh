#!/usr/bin/env bash

cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/run && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=INFO && export FNCS_TRACE=yes && export FNCS_BROKER=tcp://*:5570 && exec fncs_broker 2 &> broker.log &

cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/GLD_1/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=INFO && export FNCS_BROKER=tcp://localhost:5570 && exec gridlabd IEEE_123_feeder_1_DER_demo-recorders_Rev.glm &> glm.log &

cd ~/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/Python_Wrapper/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=INFO && export FNCS_BROKER=tcp://localhost:5570 && export FNCS_CONFIG_FILE=fncs.zpl && exec python3.6 cosim_manager.py 1510 cosim_manager.txt &> cosim_manager.log &

wait 
 
exit 0 
