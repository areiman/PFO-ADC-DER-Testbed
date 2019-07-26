import sys
# import fncs
import matlab.engine
from matlab import double as MATRIX
import csv
import numpy as np

import re

import random as rand
from random import gauss
from random import uniform
# import numpy as np
from math import sqrt

# for archiving cosim output - especially PFO output
import cosim_archiver as archive

# Start up the matlab engine
eng = matlab.engine.start_matlab()

# These objects will track persistent data
mem = {}
ewh_ranges = {}
ac_ranges = {}
pv_ranges = {}
batt_ranges = {}
Fadc_vec = {}
Dadc_vec = {}
Popt_vec = {}
Qopt_vec = {}
sum_Qmin = {}
sum_Qmax = {}
ewh_names = {}
ewh_prated = {}
ewh_qrated = {}
ewh_state = {}
pv_names = {}
batt_names = {}
ac_names = {}

para_Tmin = {}
para_Tmax = {}
para_Tdesired = {}
para_ratio = {}
para_power = {}
para_C_a = {}
para_C_m = {}
para_H_m = {}
para_U_A = {}
para_mass_internal_gain_fraction = {}
para_mass_solar_gain_fraction = {}
Q_h = {}
Q_i = {}
Q_s = {}
Dtemp = {}
halfband = {}
Dstatus = {}
P_h = {}
P_cap = {}
mdt = {}
T_out = {}

# This object will track persistent data
buff = {}
buff['AC_Tdesired'] = {}
buff['ADC_AC_P_h'] = {}
buff['AC_para_ratio'] = {}
buff['AC_Qh'] = {}


def oprint(dat, adc, t, o):
    print("Object:")
    for p in dat[adc][t][o]:
        print("\tdat[" + adc + "][" + t + "][" + o + "][" + p + "]: " + str(dat[adc][t][o][p]))


def synch(dat, timestamp=None):
    pub_dat = {}

    eng.eval('addpath ../ADC/test', nargout=0)
    #	eng.hello('you',nargout=0)
    eng.eval('addpath ../ADC/ADC_flex', nargout=0)
    eng.eval('addpath ../ADC/ADC_AC', nargout=0)
    eng.eval('addpath ../ADC/ADC_NREL', nargout=0)

    # -------------------------------------------------------------------------
    # PROCESS UPDATE PERSISTENT DATA
    # -------------------------------------------------------------------------
    for adc in dat:
        if not re.search('NONE', adc):
            if adc not in mem:
                mem[adc] = {}
                archive.init_adc(adc)
            for t in dat[adc]:
                if t not in mem[adc]:
                    mem[adc][t] = {}
                for o in sorted(dat[adc][t].keys()):
                    if o not in mem[adc][t]:
                        mem[adc][t][o] = {}
                    for p in dat[adc][t][o]:
                        mem[adc][t][o][p] = dat[adc][t][o][p]
    for adc in mem:
        print(adc)
    # sys.exit()
    # Store the desired AC temperatures
    rand.seed(None)
    for adc in dat:
        if not re.search('NONE', adc):
            for o in sorted(dat[adc]['HVAC'].keys()):
                if o not in buff['AC_Tdesired']:
                    buff['AC_Tdesired'][o] = dat[adc]['HVAC'][o]['cooling_setpoint']
                # Randomize the desired temperature
                # buff['AC_Tdesired'][o] = uniform(65, 75)
                if o not in buff['AC_para_ratio']:
                    buff['AC_para_ratio'][o] = uniform(0.5, 15)
            if adc not in buff['ADC_AC_P_h']:
                with open('Ph_hvac.csv') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        buff['ADC_AC_P_h'][adc] = [float(s) for s in row]

    # Read the Qh table
    with open("Qh_norm.csv", 'r') as Qh_f:
        headers = Qh_f.readline()
        Qhs = Qh_f.readline()
        headers = re.sub('\s', '', headers)
        Qhs = re.sub('\s', '', Qhs)
        headers_toks = re.split(',', headers)
        Qh_toks = re.split(',', Qhs)
        for idx in range(len(Qh_toks)):
            buff['AC_Qh'][headers_toks[idx]] = float(Qh_toks[idx])
    # print(buff['AC_Qh'])
    # sys.exit()
    with open("../PFO/ieee123_flex.csv", 'w+') as flex_in:
        flex_in.write("node_name, A, b\n")
    # -------------------------------------------------------------------------
    # ITERATE OVER UPDATED ADCS
    # -------------------------------------------------------------------------
    for adc in mem:
        #	for adc in ['M1_ADC12']:
        # Initialize the publish object
        pub_dat[adc] = {}
        #	if (1):
        #		adc = 'M1_ADC12'
        print("\n---------------------------------------")
        print(adc)
        print("\nIntialization and Aggregation")
        print("---------------------------------------")

        # Set up the water heaters
        t = "WH"
        ewh_names[adc] = []
        ewh_prated[adc] = []
        ewh_qrated[adc] = []
        ewh_state[adc] = []
        for o in sorted(mem[adc][t].keys()):
            # oprint(mem,adc,t,o)
            ewh_names[adc].append(o)
            ewh_prated[adc].append(mem[adc][t][o]["heating_element_capacity"])
            ewh_qrated[adc].append(0.0)
            ewh_state[adc].append(mem[adc][t][o]["is_waterheater_on"])

        # Set up HVAC systems
        t = "HVAC"
        ac_names[adc] = []
        ac_prated = []
        ac_powfac = []
        ac_qrated = []
        ac_temp = []
        ac_heat_set = []
        ac_cool_set = []
        ac_deadband = []
        for o in sorted(mem[adc][t].keys()):
            if "heating_setpoint" not in mem[adc][t][o]:
                mem[adc][t][o]["heating_setpoint"] = 65
            if "cooling_setpoint" not in mem[adc][t][o]:
                mem[adc][t][o]["cooling_setpoint"] = 72
            # oprint(mem,adc,t,o)
            ac_names[adc].append(o)
            ac_prated.append(mem[adc][t][o]["cooling_demand"] + \
                             mem[adc][t][o]["fan_design_power"] / 1000)
            ac_powfac.append(0.704)  # 0.6197
            ac_qrated.append(0.704 * ac_prated[-1])
            ac_temp.append(mem[adc][t][o]["air_temperature"])
            ac_heat_set.append(mem[adc][t][o]["heating_setpoint"])
            ac_cool_set.append(mem[adc][t][o]["cooling_setpoint"])
            ac_deadband.append(mem[adc][t][o]["thermostat_deadband"])

        # Set up batteries (o is the inverter)
        t = "BATT"
        batt_names[adc] = []
        batt_prated = []
        batt_invcap = []
        batt_qrated = []
        for o in sorted(mem[adc][t].keys()):
            # oprint(mem,adc,t,o)
            batt_names[adc].append(o)
            batt_prated.append(mem[adc][t][o]["battery.rated_power"] / 1000)
            batt_invcap.append(mem[adc][t][o]["inverter.rated_power"] / 1000)
            batt_qrated.append(mem[adc][t][o]["battery.rated_power"] / 1000)

        # Set up PV systems (o is the inverter)
        t = "PV"
        pv_names[adc] = []
        pv_pgenmax = []
        pv_invcap = []
        pv_prated = []
        pv_qrated = []
        for o in sorted(mem[adc][t].keys()):
            # oprint(mem,adc,t,o)
            pv_names[adc].append(o)
            # pv_pgenmax.append(mem[adc][t][o]["solar.rated_power"] / 1000)
            pv_pgenmax.append(mem[adc][t][o]["solar.VA_Out"] / 1000)
            pv_invcap.append(mem[adc][t][o]["solar.rated_power"] / 1000)
            pv_prated.append(mem[adc][t][o]["solar.rated_power"] / 1000)
            pv_qrated.append(mem[adc][t][o]["solar.rated_power"] / 1000)

        # DUMMY: Run task 2.1 ADC domain approximation
        # eng.eval('help basic_2_1',nargout=0)
        # eng.eval('help basic_2_1_vec',nargout=0)
        # FandD = eng.basic_2_1_vec(ewh_names,ewh_prated,\
        # 	ac_names,ac_prated,ac_powfac,\
        # 	batt_names,batt_prated,batt_invcap,\
        # 	pv_names,pv_pgenmax,pv_invcap,nargout=2)
        # Fadc = FandD[0]
        # Dadc = FandD[1]

        ## ---------------------------------------------------------------
        # ---- Bidding
        # ---------------------------------------------------------------
        # Set up inputs
        para_Tmin[adc] = []
        para_Tmax[adc] = []
        para_Tdesired[adc] = []
        para_ratio[adc] = []
        para_power[adc] = []
        para_C_a[adc] = []
        para_C_m[adc] = []
        para_H_m[adc] = []
        para_U_A[adc] = []
        para_mass_internal_gain_fraction[adc] = []
        para_mass_solar_gain_fraction[adc] = []
        Q_h[adc] = []
        Q_i[adc] = []
        Q_s[adc] = []
        Dtemp[adc] = []
        halfband[adc] = []
        Dstatus[adc] = []
        P_h[adc] = []
        P_cap[adc] = 0
        mdt[adc] = 0
        T_out[adc] = 0

        t = 'HVAC'
        for o in sorted(mem[adc][t].keys()):

            # para is a structure of vectors

            # To be randomized?
            para_Tmin[adc].append(65)  # 65 68
            para_Tmax[adc].append(75)  # 75 77

            # initial 'cooling_setpoint'
            para_Tdesired[adc].append(buff['AC_Tdesired'][o])
            # para_Tdesired.append(mem[adc][t][o]['cooling_setpoint'])

            # [0.5 to 15] uniform distribution -- to be randomized
            # para_ratio.append(1.0)
            para_ratio[adc].append(buff['AC_para_ratio'][o])

            # hvac_load
            # para_power.append(mem[adc][t][o]['hvac_load'])
            para_power[adc].append(mem[adc][t][o]["cooling_demand"] + \
                                   mem[adc][t][o]["fan_design_power"] / 1000)

            para_C_a[adc].append(mem[adc][t][o]['air_heat_capacity'])
            para_C_m[adc].append(mem[adc][t][o]['mass_heat_capacity'])
            para_H_m[adc].append(mem[adc][t][o]['mass_heat_coeff'])
            para_U_A[adc].append(mem[adc][t][o]['UA'])

            # Are these two part of the interface?
            para_mass_internal_gain_fraction[adc]. \
                append(mem[adc][t][o]['mass_internal_gain_fraction'])
            para_mass_solar_gain_fraction[adc]. \
                append(mem[adc][t][o]['mass_solar_gain_fraction'])

            # These two exist
            # Q_h[adc].append(mem[adc][t][o]['Qh'])
            Q_h[adc].append(buff['AC_Qh'][o])
            Q_i[adc].append(mem[adc][t][o]['Qi'])

            # vector of calculated values
            Q_s[adc].append(mem[adc][t][o]['incident_solar_radiation'] * \
                            mem[adc][t][o]['solar_heatgain_factor'])

            # This is a list/vector of [ air_temperature , mass_temperature ]
            Dtemp[adc].append([])
            Dtemp[adc][-1].append(mem[adc][t][o]['air_temperature'])
            Dtemp[adc][-1].append(mem[adc][t][o]['mass_temperature'])

            halfband[adc].append(mem[adc][t][o]['thermostat_deadband'] / 2.0)

            # Device status? what are the options? how do we know? historical term?
            # should be mem[adc][t][o]['is_COOL_on'] (new parameter)a
            if mem[adc][t][o]['is_COOL_on']:
                Dstatus[adc].append(1)
            else:
                Dstatus[adc].append(0)

            # T_out is the outside temperature - same for all houses
            if T_out[adc]:
                if T_out[adc] != mem[adc][t][o]['outdoor_temperature']:
                    print("WARNING: T_out is not the same for all houses")
            else:
                T_out[adc] = mem[adc][t][o]['outdoor_temperature']
        print(Q_h[adc])
        #		# Test the struct of vectors
        #		eng.PrintStructVec(para,nargout=0)
        #		sys.exit()

        # Historical price - vector of past 24 hours @ 5 minutes
        # P_h = (24 * 12 * [0.07])
        P_h[adc] = buff['ADC_AC_P_h'][adc]

        # P_cap scalar price units /[$/kW] -> 1 for $/kW; 1000 for $/MW
        P_cap[adc] = 1.0

        # Market period in hours (@5-min)
        mdt[adc] = 1 / 3600 * 300

        # Call the AC-based task 2.4 code
        #		out = eng.Task_2_4_PNNL(Q_ref,para,\
        #			Q_h,Q_i,Q_s,Dtemp,halfband,Dstatus,P_h,P_cap,mdt,nargout=2)
        # Parse outputs from the ac-based task 2.4 code
        #		T_set = out[0]
        #		P_h = out[1]
        print('*** Task2.4 Parameters bid_vec for time: ', timestamp, ' ****')
        print('		para_Tdesired= ', para_Tdesired[adc])
        print('		para_ratio= ', para_ratio[adc])
        print('		para_power= ', para_power[adc])
        print('		para_C_a= ', para_C_a[adc])
        print('		para_C_m= ', para_C_m[adc])
        print('		para_H_m= ', para_H_m[adc])
        print('		para_U_A= ', para_U_A[adc])
        print('		para_mass_internal_gain_fraction= ', para_mass_internal_gain_fraction[adc])
        print('		para_mass_solar_gain_fraction= ', para_mass_solar_gain_fraction[adc])
        print('		Q_h= ', Q_h[adc])
        print('		Q_i= ', Q_i[adc])
        print('		Q_s= ', Q_s[adc])
        print('		Dtemp= ', Dtemp[adc])
        print('		halfband= ', halfband[adc])
        print('		Dstatus= ', Dstatus[adc])
        print('		P_h= ', P_h[adc])
        print('		len(P_h)= ', len(P_h[adc]))
        print('		P_cap= ', P_cap[adc])
        print('		mdt= ', mdt[adc])
        print('		T_out= ', T_out[adc])

        out = eng.Task_2_4_PNNL_bid_vec(para_Tmin[adc], para_Tmax[adc], para_Tdesired[adc], para_ratio[adc],
                                        para_power[adc], \
                                        para_C_a[adc], para_C_m[adc], para_H_m[adc], para_U_A[adc], \
                                        para_mass_internal_gain_fraction[adc], para_mass_solar_gain_fraction[adc], \
                                        Q_h[adc], Q_i[adc], Q_s[adc], Dtemp[adc], halfband[adc], Dstatus[adc], P_h[adc],
                                        P_cap[adc], mdt[adc], T_out[adc], \
                                        nargout=2)
        sum_Qmax[adc] = out[0]
        sum_Qmin[adc] = out[1]
        print("*** sum_Qmax *** = ", sum_Qmax[adc])
        print("*** sum_Qmin *** = ", sum_Qmin[adc])
        # sys.exit()

        # ---------------------------------------------------------------
        # ---- Aggregation Task 2.1
        # ---------------------------------------------------------------
        # """
        print("Device totals:")
        print("    {} electric water heaters".format(len(ewh_names[adc])))
        print("    {} air conditioners".format(len(ac_names[adc])))
        print("    {} photovoltaic systems".format(len(pv_names[adc])))
        print("    {} battery systems".format(len(batt_names[adc])))
        # print(ewh_names[adc])
        print(ac_names[adc])
        # print(pv_names[adc])
        # print(batt_names[adc])
        area_scale_factor = 0.5
        flex_agg = eng.testbed_2_1_vec(ewh_names[adc], ewh_prated[adc], \
                                       ac_names[adc], ac_prated, ac_powfac, \
                                       batt_names[adc], batt_prated, batt_invcap, \
                                       pv_names[adc], pv_pgenmax, pv_invcap, sum_Qmax[adc], sum_Qmin[adc],
                                       area_scale_factor, nargout=6)
        Fadc = flex_agg[0]
        Dadc = flex_agg[1]
        ewh_range = flex_agg[2]
        ac_range = flex_agg[3]
        pv_range = flex_agg[4]
        batt_range = flex_agg[5]
        #		print("Fadc is: "+str(Fadc))
        #		print("Dadc is: "+str(Dadc))
        #		print("Ranges:")
        #		print(ewh_range)
        print(ac_range)
        # print(pv_range)
        # print(batt_range)

        ewh_ranges[adc] = ewh_range
        ac_ranges[adc] = ac_range
        pv_ranges[adc] = pv_range
        batt_ranges[adc] = batt_range
        Fadc_vec[adc] = Fadc
        Dadc_vec[adc] = Dadc

        # writing flex outputs in input file for PFO julia function
        tempD = str(Dadc).replace('],[', '|')
        tempD = tempD.replace('[[', '[')
        tempD = tempD.replace(']]', ']')
        tempF = str(Fadc).replace('],[', '|')
        tempF = tempF.replace('[[', '[')
        tempF = tempF.replace(']]', ']')
        tempF = tempF.replace(',', ' ')
        with open("../PFO/ieee123_flex.csv", 'a+') as flex_in:
            flex_in.write(adc + ',' + tempF + ',' + tempD + '\n')
    # sys.exit()

    # """
    # ---------------------------------------------------------------------
    # PFO EMULATOR
    # ---------------------------------------------------------------------
    # Assuming rectangular flexibility
    for adc in mem:
        print("\n---------------------------------------")
        print(adc)
        print("\nPFO Emulator")
        print("---------------------------------------")
        rand.seed(None)  # seed with system time
        #		tmp = MATRIX([[-1.0,0.0],[0.0,-1.0],[1.0,0.0],[0.0,1.0]])
        #		print(tmp)
        if Fadc_vec[adc][0][0] == -1.0 and Fadc_vec[adc][0][1] == 0.0 \
                and Fadc_vec[adc][1][0] == 0.0 and Fadc_vec[adc][1][1] == -1.0 \
                and Fadc_vec[adc][2][0] == 1.0 and Fadc_vec[adc][2][1] == 0.0 \
                and Fadc_vec[adc][3][0] == 0.0 and Fadc_vec[adc][3][1] == 1.0:
            Popt_vec[adc] = (Dadc_vec[adc][0][0] + Dadc_vec[adc][2][0]) / 2.0 * (1 + gauss(0, 1) / 3.0)
            if Popt_vec[adc] > Dadc_vec[adc][2][0]:
                Popt_vec[adc] = Dadc_vec[adc][2][0]
            if Popt_vec[adc] < -1 * Dadc_vec[adc][0][0]:
                Popt_vec[adc] = -1 * Dadc_vec[adc][0][0]
            Qopt_vec[adc] = (Dadc_vec[adc][1][0] + Dadc_vec[adc][3][0]) / 2.0 * (1 + gauss(0, 1) / 3.0)
            if Qopt_vec[adc] > Dadc_vec[adc][3][0]:
                Qopt_vec[adc] = Dadc_vec[adc][3][0]
            if Qopt_vec[adc] < -1 * Dadc_vec[adc][1][0]:
                Qopt_vec[adc] = -1 * Dadc_vec[adc][1][0]
        elif Fadc_vec[adc][0][0] == 1.0 and Fadc_vec[adc][0][1] == 0.0 \
                and Fadc_vec[adc][1][0] == -1.0 and Fadc_vec[adc][1][1] == 0.0 \
                and Fadc_vec[adc][2][0] == 0.0 and Fadc_vec[adc][2][1] == 1.0 \
                and Fadc_vec[adc][3][0] == 0.0 and Fadc_vec[adc][3][1] == -1.0:
            Popt_vec[adc] = (Dadc_vec[adc][0][0] + Dadc_vec[adc][1][0]) / 2.0 * (1 + gauss(0, 1) / 3.0)
            if Popt_vec[adc] > Dadc_vec[adc][0][0]:
                Popt_vec[adc] = Dadc_vec[adc][0][0]
            if Popt_vec[adc] < -1 * Dadc_vec[adc][1][0]:
                Popt_vec[adc] = -1 * Dadc_vec[adc][1][0]
            Qopt_vec[adc] = (Dadc_vec[adc][2][0] + Dadc_vec[adc][3][0]) / 2.0 * (1 + gauss(0, 1) / 3.0)
            if Qopt_vec[adc] > Dadc_vec[adc][2][0]:
                Qopt_vec[adc] = Dadc_vec[adc][2][0]
            if Qopt_vec[adc] < -1 * Dadc_vec[adc][3][0]:
                Qopt_vec[adc] = -1 * Dadc_vec[adc][3][0]
        else:
            print("Error: unexpected Fadc")
            exit()
        print("Popt is " + str(Popt_vec[adc]))
        print("Qopt is " + str(Qopt_vec[adc]))

    # Reading Julia PFO output file
    Popt_vec1 = {}
    Qopt_vec1 = {}
    with open("../PFO/output.csv", 'r') as pfo_out:
        next(pfo_out)
        csv_reader = csv.reader(pfo_out)
        for row in csv_reader:
            Popt_vec1[row[0]] = row[1]
            Qopt_vec1[row[0]] = row[2]

    for adc in mem:
        # ----------------------------------------------------------------------
        # DISAGGREGATION
        # ----------------------------------------------------------------------
        print("\n---------------------------------------")
        print(adc)
        print("\nDisaggregation and Dispatch")
        print("---------------------------------------")
        eng.eval('addpath ../ADC/ADC_flex/functions', nargout=0)
        disagg_dispatch = eng.disaggregation(MATRIX([[Popt_vec[adc], Qopt_vec[adc]]]), \
                                             ewh_ranges[adc], ac_ranges[adc], pv_ranges[adc], batt_ranges[adc], \
                                             nargout=5)

        Popt_ewh = disagg_dispatch[0][0][0]
        Qopt_ewh = disagg_dispatch[0][0][1]
        print("    Popt_ewh is: " + str(Popt_ewh))
        print("    Qopt_ewh is: " + str(Qopt_ewh))
        Popt_ac = disagg_dispatch[1][0][0]
        Qopt_ac = disagg_dispatch[1][0][1]
        print("    Popt_ac is: " + str(Popt_ac))
        print("    Qopt_ac is: " + str(Qopt_ac))
        Popt_pv = disagg_dispatch[2][0][0]
        Qopt_pv = disagg_dispatch[2][0][1]
        print("    Popt_pv is: " + str(Popt_pv))
        print("    Qopt_pv is: " + str(Qopt_pv))
        Popt_batt = disagg_dispatch[3][0][0]
        Qopt_batt = disagg_dispatch[3][0][1]
        print("    Popt_batt is: " + str(Popt_batt))
        print("    Qopt_batt is: " + str(Qopt_batt))
        Popt_unserved = disagg_dispatch[4][0][0]
        Qopt_unserved = disagg_dispatch[4][0][1]
        print("    Popt_unserved is: " + str(Popt_unserved))
        print("    Qopt_unserved is: " + str(Qopt_unserved))
        # sys.exit()
        # ----------------------------------------------------------------------
        # ARCHIVE AGGREGATE AND DISAGGREGATED PFO OUTPUT
        # ----------------------------------------------------------------------
        archive.archive_pfo(adc, timestamp, Popt_vec[adc], Qopt_vec[adc], \
                            Popt_ewh, Qopt_ewh, Popt_ac, \
                            Qopt_ac, Popt_batt, Qopt_batt, Popt_pv, Qopt_pv, Popt_unserved, Qopt_unserved,
                            sum_Qmax[adc], sum_Qmin[adc])
        #		archive.archive_pfo(adc,timestamp,Popt,Qopt)

        # ----------------------------------------------------------------------
        # DUMMY TASK 2.4 - DER DISPATCH
        # ----------------------------------------------------------------------
        '''
		# Call the dummy task 2.4 code
		new_state = eng.basic_2_4(Popt, Qopt, ewh_state, \
			ac_temp, ac_heat_set, ac_cool_set, ac_deadband, \
			ewh_prated, ewh_qrated, ac_prated, ac_qrated, \
			batt_prated, batt_qrated, pv_prated, pv_prated, nargout=7)
		# parse the outputs
		new_ewh_tank_setpoint = new_state[0]
		new_ac_heat_set = new_state[1]
		new_ac_cool_set = new_state[2]
		batt_p = new_state[3]; batt_q = new_state[4]
		pv_p = new_state[5]; pv_q = new_state[6]

		# print(new_state)


#		### FOR DEBUGGING: ARCHIVE AGGREGATE AND DISAGGREGATED PFO OUTPUT
#		### NEEDS TO BE DELETED IN PRODUCTION VERSION
#		if adc == 'M1_ADC90':
#			print("calling cosim archiver for adc ", adc)
#			print(new_ewh_tank_setpoint)
#		ac_off_set = 212
#		ewh_off_set = 32
#		n_ewh_ON = np.count_nonzero(np.array(new_ewh_tank_setpoint) - ewh_off_set)
#		n_ac_ON = np.count_nonzero(np.array(new_ac_cool_set) - ac_off_set)
#		# ac_p = np.mean(ac_prated)*n_ac_ON
#		ac_p = sum(np.multiply(np.array(ac_prated),\
#			(np.array(new_ac_cool_set._data) - ac_off_set))) / (32 - ac_off_set)
#		# ac_q = np.mean(ac_qrated)*n_ac_ON
#		ac_q = sum(np.multiply(np.array(ac_qrated),\
#			(np.array(new_ac_cool_set._data) - ac_off_set))) / (32 - ac_off_set)
#		# ewh_p = np.mean(ewh_prated)*n_ewh_ON
#		ewh_p = sum(np.multiply(np.array(ewh_prated),\
#			(np.array(new_ewh_tank_setpoint._data) - ewh_off_set))) / (
#			212 - ewh_off_set)
#		# ewh_q = np.mean(ewh_qrated)*n_ewh_ON
#		ewh_q = sum(np.multiply(np.array(ewh_qrated),\
#			(np.array(new_ewh_tank_setpoint._data) - ac_off_set))) / (
#			212 - ewh_off_set)
#		archive.archive_pfo_dummy(adc, timestamp, Popt, Qopt, np.sum(batt_p),\
#			np.sum(batt_q), np.sum(pv_p),\
#			np.sum(pv_q), ac_p, ac_q, ewh_p, ewh_q, n_ac_ON, n_ewh_ON)
#		### END DEBUGGING SECTION

		# Populate water heaters in the publish object
		t = "WH"
		pub_dat[adc][t] = {}
		# print(new_ewh_tank_setpoint)
		if len(ewh_names) == 1:
			o = ewh_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint
			if new_ewh_tank_setpoint == 212:
				pub_dat[adc][t][o]["re_override"] = 1
			elif new_ewh_tank_setpoint == 32:
				pub_dat[adc][t][o]["re_override"] = 2
		else:
			for idx in range(len(ewh_names)):
				# print('\t'+str(idx))
				o = ewh_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint[idx][0]
				if new_ewh_tank_setpoint[idx][0] == 212:
					pub_dat[adc][t][o]["re_override"] = 1
				elif new_ewh_tank_setpoint[idx][0] == 32:
					pub_dat[adc][t][o]["re_override"] = 2

		# Populate the HVACs in the publish object
		t = "HVAC"
		pub_dat[adc][t] = {}
		if len(ac_names) == 1:
			o = ac_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["cooling_setpoint"] = new_ac_cool_set
			pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set
		else:
			for idx in range(len(ac_names)):
				o = ac_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["cooling_setpoint"] = new_ac_cool_set[idx][0]
				pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set[idx][0]

		# Populate the battery inverters in the publish object
		t = "BATT"
		pub_dat[adc][t] = {}
		# print(batt_p)
		if len(batt_names) == 1:
			o = batt_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = batt_p*1000
			pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q*1000
		else:
			for idx in range(len(batt_names)):
				# print('\t'+str(idx))
				o = batt_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = batt_p[idx][0]*1000
				pub_dat[adc][t][o]["inverter.Q_Out"] = batt_q[idx][0]*1000

		# Populate the PV inverters
		t = "PV"
		pub_dat[adc][t] = {}
		# print('\t'+str(pv_p))
		if len(pv_names) == 1:
			o = pv_names[0]
			pub_dat[adc][t][o] = {}
			pub_dat[adc][t][o]["inverter.P_Out"] = pv_p*1000
			pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q*1000
		else:
			for idx in range(len(pv_names)):
				# print(idx)
				o = pv_names[idx]
				pub_dat[adc][t][o] = {}
				pub_dat[adc][t][o]["inverter.P_Out"] = pv_p[idx][0]*1000
				pub_dat[adc][t][o]["inverter.Q_Out"] = pv_q[idx][0]*1000

		'''
        # ---------------------------------------------------------------------
        # DER DISPATCH FOR EWH
        # ---------------------------------------------------------------------
        # To be taken from dummy implementation

        # Call the actual task 2.4 for ewh code
        new_ewh_tank_setpoint = eng.Task_2_4_ewh(ewh_state[adc], ewh_prated[adc], Popt_ewh)
        print("**new ewh tank setpoint**")
        print(new_ewh_tank_setpoint)
        # Populate water heaters in the publish object
        t = "WH"
        pub_dat[adc][t] = {}
        # print(new_ewh_tank_setpoint)
        if len(ewh_names[adc]) == 1:
            o = ewh_names[adc][0]
            pub_dat[adc][t][o] = {}
            pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint
            if new_ewh_tank_setpoint == 212:
                pub_dat[adc][t][o]["re_override"] = 1
            elif new_ewh_tank_setpoint == 32:
                pub_dat[adc][t][o]["re_override"] = 2
        else:
            for idx in range(len(ewh_names[adc])):
                # print('\t'+str(idx))
                o = ewh_names[adc][idx]
                pub_dat[adc][t][o] = {}
                pub_dat[adc][t][o]["tank_setpoint"] = new_ewh_tank_setpoint[idx][0]
                if new_ewh_tank_setpoint[idx][0] == 212:
                    pub_dat[adc][t][o]["re_override"] = 1
                elif new_ewh_tank_setpoint[idx][0] == 32:
                    pub_dat[adc][t][o]["re_override"] = 2

        # ----------------------------------------------------------------------
        # DER DISPATCH FOR HVAC
        # ----------------------------------------------------------------------

        # Set up inputs
        Q_ref = Popt_ac

        print('*** Task2.4 Parameters clear_vec for time: ', timestamp, ' ****')
        print('		Q_ref = ', Q_ref)
        print('		para_Tdesired= ', para_Tdesired[adc])
        print('		para_ratio= ', para_ratio[adc])
        print('		para_power= ', para_power[adc])
        print('		para_C_a= ', para_C_a[adc])
        print('		para_C_m= ', para_C_m[adc])
        print('		para_H_m= ', para_H_m[adc])
        print('		para_U_A= ', para_U_A[adc])
        print('		para_mass_internal_gain_fraction= ', para_mass_internal_gain_fraction[adc])
        print('		para_mass_solar_gain_fraction= ', para_mass_solar_gain_fraction[adc])
        print('		Q_h= ', Q_h[adc])
        print('		Q_i= ', Q_i[adc])
        print('		Q_s= ', Q_s[adc])
        print('		Dtemp= ', Dtemp[adc])
        print('		halfband= ', halfband[adc])
        print('		Dstatus= ', Dstatus[adc])
        print('		P_h= ', P_h[adc])
        print('		len(P_h)= ', len(P_h[adc]))
        print('		P_cap= ', P_cap[adc])
        print('		mdt= ', mdt[adc])
        print('		T_out= ', T_out[adc])

        out = eng.Task_2_4_PNNL_clear_vec(Q_ref, \
                                          para_Tmin[adc], para_Tmax[adc], para_Tdesired[adc], para_ratio[adc],
                                          para_power[adc], para_C_a[adc], para_C_m[adc], para_H_m[adc], para_U_A[adc], \
                                          para_mass_internal_gain_fraction[adc], para_mass_solar_gain_fraction[adc], \
                                          Q_h[adc], Q_i[adc], Q_s[adc], Dtemp[adc], halfband[adc], Dstatus[adc],
                                          P_h[adc], P_cap[adc], mdt[adc], T_out[adc], \
                                          nargout=2)

        T_set = out[0]
        # P_h = out[1][0]
        # P_h = P_h._data.tolist()
        buff['ADC_AC_P_h'][adc] = out[1][0]._data.tolist()
        print("**** ")
        print("*** HVAC output P_h ****  = ", buff['ADC_AC_P_h'][adc])
        # sys.exit()

        t = "HVAC"
        pub_dat[adc][t] = {}
        if len(ac_names[adc]) == 1:
            o = ac_names[adc][0]
            pub_dat[adc][t][o] = {}
            pub_dat[adc][t][o]["cooling_setpoint"] = T_set[idx][0]
        # pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set
        else:
            for idx in range(len(ac_names[adc])):
                o = ac_names[adc][idx]
                pub_dat[adc][t][o] = {}
                pub_dat[adc][t][o]["cooling_setpoint"] = T_set[idx][0]
        # pub_dat[adc][t][o]["heating_setpoint"] = new_ac_heat_set[idx][0]

        # ----------------------------------------------------------------------
        # TASK 2.4 FOR PV AND BATTERIES
        # ----------------------------------------------------------------------
        # '''
        # Control time
        #		deltat = 30.0
        deltat = 4.0  # 4-second control time step

        # PV parameters
        cap_pv = []  # PV capacity
        p_av = []  # PV available power
        t = 'PV'
        n_pv = len(mem[adc][t])
        for o in sorted(mem[adc][t].keys()):
            #			print(mem[adc][t][o])
            #			sys.exit()
            cap_pv.append(mem[adc][t][o]['solar.rated_power'])
            p_av.append(mem[adc][t][o]['solar.VA_Out'])

        # Battery parameters
        cap_ba = []  # battery capacity
        cap_ba_inv = []  # battery inverter rated power
        p_ba_cha_max = []  # maximum charging rate
        p_ba_dis_max = []  # maximum discharging rate
        eff_ba = []  # battery efficiency
        SOC_set = []  # preferred SOC: 50%
        SOC_now = []  # current SOC
        t = 'BATT'
        n_ba = len(mem[adc][t])
        for o in sorted(mem[adc][t].keys()):
            #			print(mem[adc][t][o])
            #			sys.exit()
            cap_ba.append(mem[adc][t][o]['battery.battery_capacity'])
            cap_ba_inv.append(mem[adc][t][o]['inverter.rated_power'])
            p_ba_cha_max.append(mem[adc][t][o]['battery.rated_power'] * -1.0)
            p_ba_dis_max.append(mem[adc][t][o]['battery.rated_power'])
            eff_ba.append(mem[adc][t][o]['inverter.inverter_efficiency'])
            SOC_set.append(0.5)
            SOC_now.append(mem[adc][t][o]['battery.state_of_charge'])

        # Calculate the combined Popt and Qopt of PV plus batteries
        p_opt = (Popt_pv + Popt_batt) * 1000.0
        q_opt = (Qopt_pv + Qopt_batt) * 1000.0
        print("--p_opt for PV+batt: {0} W".format(p_opt))
        print("--q_pot for PV+batt: {0} VAR".format(q_opt))

        print("deltat: {0}".format(deltat))
        print("n_pv: {0}".format(n_pv))
        print("n_ba: {0}".format(n_ba))
        print("cap_pv: {0}".format(cap_pv))
        print("p_av: {0}".format(p_av))
        print("cap_ba: {0}".format(cap_ba))
        print("cap_ba_inv: {0}".format(cap_ba))
        print("p_ba_cha_max: {0}".format(p_ba_cha_max))
        print("p_ba_dis_max: {0}".format(p_ba_dis_max))
        print("eff_ba: {0}".format(eff_ba))
        print("SOC_set: {0}".format(SOC_set))
        print("SOC_now: {0}".format(SOC_now))
        print("p_opt: {0}".format(p_opt))
        print("q_opt: {0}".format(q_opt))

        # Call the PV and Battery implementation of task 2.4
        out = eng.ADC_control(deltat, n_pv, n_ba, MATRIX(cap_pv), MATRIX(p_av), \
                              MATRIX(cap_ba), MATRIX(cap_ba_inv), MATRIX(p_ba_cha_max), MATRIX(p_ba_dis_max), \
                              MATRIX(eff_ba), MATRIX(SOC_set), MATRIX(SOC_now), \
                              p_opt, q_opt, nargout=4)

        # Parse outputs
        p_pv = out[0]
        q_pv = out[1]
        p_ba = out[2]
        q_ba = out[3]

        # Populate the PV inverters
        t = "PV"
        pub_dat[adc][t] = {}
        # print('\t'+str(pv_p))
        tmp_p_pv = 0.0
        tmp_q_pv = 0.0
        if len(pv_names[adc]) == 1:
            tmp_p_pv = tmp_p_pv + p_pv
            tmp_q_pv = tmp_q_pv + q_pv
            o = pv_names[adc][0]
            pub_dat[adc][t][o] = {}
            pub_dat[adc][t][o]["inverter.P_Out"] = p_pv
            pub_dat[adc][t][o]["inverter.Q_Out"] = q_pv
        else:
            for idx in range(len(pv_names[adc])):
                # print(idx)
                tmp_p_pv = tmp_p_pv + p_pv[0][idx]
                tmp_q_pv = tmp_q_pv + q_pv[0][idx]
                o = pv_names[adc][idx]
                pub_dat[adc][t][o] = {}
                pub_dat[adc][t][o]["inverter.P_Out"] = p_pv[0][idx]
                pub_dat[adc][t][o]["inverter.Q_Out"] = q_pv[0][idx]
        print('\np_pv:'), print(p_pv)
        print("--total p_pv: {0}".format(tmp_p_pv))
        print('\nq_pv:'), print(q_pv)
        print("--total q_pv: {0}".format(tmp_q_pv))

        # Populate the battery inverters in the publish object
        t = "BATT"
        pub_dat[adc][t] = {}
        # print(batt_p)
        tmp_p_ba = 0.0
        tmp_q_ba = 0.0
        if len(batt_names[adc]) == 1:
            tmp_p_ba = tmp_p_ba + p_ba
            tmp_q_ba = tmp_q_ba + q_ba
            o = batt_names[adc][0]
            pub_dat[adc][t][o] = {}
            pub_dat[adc][t][o]["inverter.P_Out"] = p_ba
            pub_dat[adc][t][o]["inverter.Q_Out"] = q_ba
        else:
            for idx in range(len(batt_names[adc])):
                # print('\t'+str(idx))
                tmp_p_ba = tmp_p_ba + p_ba[0][idx]
                tmp_q_ba = tmp_q_ba + q_ba[0][idx]
                o = batt_names[adc][idx]
                pub_dat[adc][t][o] = {}
                pub_dat[adc][t][o]["inverter.P_Out"] = p_ba[0][idx]
                pub_dat[adc][t][o]["inverter.Q_Out"] = q_ba[0][idx]
        print('\np_ba:'), print(p_ba)
        print("--total p_ba: {0}".format(tmp_p_ba))
        print('\nq_ba:'), print(q_ba)
        print("--total q_ba: {0}".format(tmp_q_ba))

    # '''
    # --------------------------------------------------------------------------
    # RETURN THE THE PUBLISH OBJECT BACK TO THE PARSER
    # --------------------------------------------------------------------------
    return pub_dat
