'''cosim_archiver'''

import subprocess
import glob

# Create the cosim_dat directory if necessary
if '../cosim_dat' not in glob.glob('../*'):
	subprocess.run(["mkdir","../cosim_dat"])

# Clean existing logs from the CSV
for csv in glob.glob('../cosim_dat/*.csv'):
	subprocess.run(["rm",csv])

# Write the README file
with open("../cosim_dat/README.txt",'w') as fh:
	fh.write("This directory will contain logs of cosim manager output.\n\n")
	fh.write("There will be one CSV file per ADC.\n\n")
	fh.write("The columns will be:\n")
	fh.write("Timestamp,Popt,Qopt,Popt_WH,Qopt_WH,Popt_HVAC,Qopt_HVAC," +\
		"Popt_BATT,Qopt_BATT,Popt_PV,Qopt_PV\n")

def init_adc(adc):
	with open("../cosim_dat/" + adc + ".csv" , 'w') as fh:
		fh.write("Timestamp,Popt,Qopt,Popt_WH,Qopt_WH,Popt_HVAC,Qopt_HVAC," +\
			"Popt_BATT,Qopt_BATT,Popt_PV,Qopt_PV\n")

def archive_pfo(adc,timestamp,P,Q,Pwh,Qwh,Pac,Qac,Pba,Qba,Ppv,Qpv):
	with open("../cosim_dat/" + adc + ".csv" , 'a') as fh:
		fh.write(str(timestamp) + ',' +\
		str(P)   + ',' + str(Q)   + ',' +\
		str(Pwh) + ',' + str(Qwh) + ',' +\
		str(Pac) + ',' + str(Qac) + ',' +\
		str(Pba) + ',' + str(Qba) + ',' +\
		str(Ppv) + ',' + str(Qpv) + '\n')

