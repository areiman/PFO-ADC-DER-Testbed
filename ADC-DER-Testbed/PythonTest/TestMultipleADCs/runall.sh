#!/bin/bash 
 
clear 
 
cd /home/gld/FNCS_PythonTest/TestMultipleADCs/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_TRACE=yes && export FNCS_BROKER=tcp://*:5570 && exec fncs_broker 2 &> broker.log &
cd /home/gld/FNCS_PythonTest/TestMultipleADCs/GLD/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_BROKER=tcp://localhost:5570 && exec gridlabd IEEE_123_feeder_0_DER.glm &> glm.log &
cd /home/gld/FNCS_PythonTest/TestMultipleADCs/Python/ && export FNCS_LOG_STDOUT=yes && export FNCS_LOG_LEVEL=DEBUG4 && export FNCS_BROKER=tcp://localhost:5570 && FNCS_CONFIG_FILE=fncs.zpl && exec python get_states.py 60 get_states.txt &> get_states.out &

wait 
 
exit 0 
