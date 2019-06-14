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
	print("creating cosim_data csv file")
	with open("../cosim_dat/" + adc + ".csv" , 'w') as fh:
		fh.write("Timestamp,Popt,Qopt,Popt_WH,Qopt_WH,Popt_HVAC,Qopt_HVAC," +\
			"Popt_BATT,Qopt_BATT,Popt_PV,Qopt_PV\n")

def archive_pfo(adc,timestamp,P,Q,\
		Pwh=None,Qwh=None,Pac=None,Qac=None,\
		Pba=None,Qba=None,Ppv=None,Qpv=None):
	
	with open("../cosim_dat/" + adc + ".csv" , 'a') as fh:
		print("writing csv file")
		fh.write(str(timestamp) + ',' +\
		str(P)   + ',' + str(Q)   + ',' +\
		str(Pwh) + ',' + str(Qwh) + ',' +\
		str(Pac) + ',' + str(Qac) + ',' +\
		str(Pba) + ',' + str(Qba) + ',' +\
		str(Ppv) + ',' + str(Qpv) + '\n')

def init_adc_dummy(adc):
	print("creating cosim_data csv file")
	with open("../cosim_dat/" + adc + ".csv" , 'w') as fh:
		fh.write(
			"Timestamp,Popt,Qopt,Popt_BATT,Qopt_BATT,Popt_PV,Qopt_PV,Popt_HVAC,Qopt_HVAC,Popt_WH,Qopt_WH,n_ac_ON,n_ewh_ON\n")

def archive_pfo_dummy(adc, timestamp, P, Q, batt_p, batt_q, pv_p, pv_q, ac_p, ac_q, ewh_p, ewh_q, n_ac_ON, n_ewh_ON):
	print("inside cosim archiver.....")
	with open("../cosim_dat/" + adc + ".csv" , 'a') as fh:
		print("writing csv file")
		fh.write(str(timestamp) + ',' +\
		str(P)   + ',' + str(Q)   + ',' +\
		# str(tank_setpoint) + ',' +\
		# str(heat_set) + ',' + str(cool_set) + ',' +\
		str(batt_p) + ',' + str(batt_q) + ',' +\
		str(pv_p) + ',' + str(pv_q) + ',' +\
		str(ac_p) + ',' + str(ac_q) + ',' + \
		str(ewh_p) + ',' + str(ewh_q) + ',' + \
		str(n_ac_ON) + ',' + str(n_ewh_ON) + '\n')


