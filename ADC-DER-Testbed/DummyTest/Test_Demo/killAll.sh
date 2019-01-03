#!/bin/bash

clear

#pkill -9 fncs_broker
#pkill -9 gridlabd
#pkill -9 python
cd /home/gld/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo/ killall fncs_broker
cd /home/gld/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo/ killall gridlabd
cd /home/gld/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo/ killall python
cd /home/gld/PFO-ADC-DER-Testbed/ADC-DER-Testbed/DummyTest/Test_Demo/ killall matlab

exit 0
