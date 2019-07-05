# This is to read and store csv data from gld into a dictionary and save as json file
import json;
import sys;
import numpy as np;
import csv;
import glob
import os

cwd = os.getcwd()
os.chdir('/home/ankit/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/post_process')

## Readinf gld csv files
csv_path = './../GLD/output/recorder_*.csv'
skip_filenames = ['./../GLD/output/recorder_wh_heat_mode.csv',
                  './../GLD/output/recorder_hvac_cooling_system_type.csv',
                  './../GLD/output/recorder_hvac_auxiliary_system_type.csv',
                  './../GLD/output/recorder_battInv_max_charge_rate.csv',
                  './../GLD/output/recorder_battInv_inverter_efficiency.csv',
                  './../GLD/output/recorder_batt_battery_capacity.csv',
                  './../GLD/output/recorder_hvac_heating_system_type.csv']
# region Reading csv into a dictionary
temp_dict1={}
gld_data = {}
gld_data['batt'] = {}
gld_data['battInv'] = {}
gld_data['hvac'] = {}
gld_data['wh'] = {}
gld_data['solar'] = {}
gld_data['solarInv'] = {}


for fname in glob.glob(csv_path):
    if fname in skip_filenames:
        continue
    print(fname)
    splt = fname.split('recorder_')[1]
    DER_type = splt.split('_',1)[0]
    property = splt.split('_',1)[1][0:-4]
    values = []
    time =[]
    temp_dict = {}
    with open(fname, mode='r') as csv_file:
        for i in range(8):
            next(csv_file)
        csv_reader = csv.reader(csv_file)
        header_line = 1
        for row in csv_reader:
            if row[0] == '# end of file':
                break
            if header_line:
                temp_dict['object_name'] = row[1:]
                header_line = 0
            else:
                time.append(row[0])
                values.append(row[1:])
        if len(values) > 1 and len(values[-1]) != len(values[-2]):
            values.pop()
        values= np.array(values)
        if 'i' in values[0][0] or 'j' in values[0][0]:
            values = [[(ss.replace('i', 'j')) for ss in s] for s in values]
            #values = list(map(cfloat, values))
        else:
            values = [[float(ss) for ss in s] for s in values]
        temp_dict['values'] = values
        temp_dict['time'] = time
    gld_data[DER_type][property] = temp_dict

with open('./gld_data.json', 'w') as fp:
    json.dump(gld_data, fp, sort_keys=True, indent=4)
# endregion

# Reading cosim_data csv files from cosim_dat folder
#os.chdir('/home/ankit/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/post_process')
csv_path = './../cosim_dat/M1_*.csv'
skip_filenames = []
cosim_data={}
for fname in glob.glob(csv_path):
    if fname in skip_filenames:
        continue
    print(fname)
    splt = fname.split('M1_')[1]
    adc_num = splt.split('.')[0][3:]
    if adc_num not in cosim_data:
        cosim_data[adc_num] = {}
        # PQ_opt[adc_num]['Popt'] = []
        # PQ_opt[adc_num]['Qopt'] = []
    values = []
    time =[]
    temp_dict = {}
    with open(fname, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header_line = 1
        for row in csv_reader:
            if header_line:
                header = []
                for i in row:
                    cosim_data[adc_num][i] = []
                    header.append(i)
                header_line = 0
            else:
                for j in range(0,len(row)):
                    if row[j] != 'None':
                        cosim_data[adc_num][header[j]].append(float(row[j]))

with open('./cosim_data.json', 'w') as fp:
    json.dump(cosim_data, fp, sort_keys=True, indent=4)
