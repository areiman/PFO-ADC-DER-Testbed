import json
import numpy as np
import matplotlib as mpl;
import matplotlib.pyplot as plt;
import csv
import time
import copy

#loading cosim_manager data
lp = open('./Python_Wrapper/cosim_data.json').read()
cosim_data = json.loads(lp)
PQ_opt={}
PQ_opt['time'] = []
times = list(map(int, list(cosim_data.keys())))
times.sort()
for t in times:
    PQ_opt['time'].append(t)
    for adc_name in cosim_data[str(t)]:
        adc_num = adc_name.split('_ADC')[1]
        if adc_num not in PQ_opt:
            PQ_opt[adc_num]={}
            PQ_opt[adc_num]['Popt'] = []
            PQ_opt[adc_num]['Qopt'] = []
        PQ_opt[adc_num]['Popt'].append(cosim_data[str(t)][adc_name][0]/1000)
        PQ_opt[adc_num]['Qopt'].append(cosim_data[str(t)][adc_name][1]/1000)

# create mapping of each node to its ADC
adc_nodes_map=[]
adc_file = "./../../GLD/initial_scenario/ADC_Location/ADC_Placement_by_Voltage_Drop.csv"
with open(adc_file, mode='r') as csv_file:
    for i in range(1):
        next(csv_file)
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        adc_nodes_map.append([row[0], row[-1]])
adc_nodes_map = np.array(adc_nodes_map)

#function to return adc name of the input node
def find_adc(node, adc_nodes_map=adc_nodes_map):
    ind = np.where(adc_nodes_map[:,0]==node)[0][0]
    return adc_nodes_map[ind,1]

# Loading gld_data.json
lp = open('gld_data.json').read()
gld_data = json.loads(lp)

# creating a dict to map each adc to the indexes of devices in gld_data for each der type
# adc['der']['adc name']=[indexes in the gld data]
# t=time.time()
# adc_ind = {}
# der_type=[['battInv', 'power'], ['solarInv','power'], ['hvac','power'], ['wh','power']]
# for der in der_type:
#     adc_ind[der[0]] = {}
#     obj = gld_data[der[0]][der[1]]['object_name']
#     for a in obj:
#         b = a.split('_')[-2][1:]
#         # if 'l102_tm' in a:
#         if find_adc(b) not in adc_ind[der[0]]:
#             adc_ind[der[0]][find_adc(b)] = []
#         adc_ind[der[0]][find_adc(b)].append(obj.index(a))
# print('elapsed time is ',time.time()-t)

# creating a dict to map each adc to the indexes of devices in gld_data for each der type
# adc_ind['adc name']['der']=[indexes in the gld data]
t=time.time()
adc_ind = {}
der_type=[['battInv', 'power'], ['solarInv','power'], ['hvac','power'], ['wh','power']]
for der in der_type:
    obj = gld_data[der[0]][der[1]]['object_name']
    for a in obj:
        b = a.split('_')[-2][1:]
        # if 'l102_tm' in a:
        if find_adc(b) not in adc_ind:
            adc_ind[find_adc(b)] = {}
        if der[0] not in adc_ind[find_adc(b)]:
            adc_ind[find_adc(b)][der[0]]=[]
        adc_ind[find_adc(b)][der[0]].append(obj.index(a))
print('elapsed time is ',time.time()-t)

# Actuation Signals
#hrs = gld_data['battInv']['P_Out']['time']
battInv_Pout = np.array(gld_data['battInv']['P_Out']['values']).astype(np.float)
battInv_Qout = np.array(gld_data['battInv']['Q_Out']['values']).astype(np.float)
solarInv_Pout = np.array(gld_data['solarInv']['P_Out']['values']).astype(np.float)
solarInv_Qout = np.array(gld_data['solarInv']['Q_Out']['values']).astype(np.float)
hvac_seth = np.array(gld_data['hvac']['heating_setpoint']['values']).astype(np.float)
hvac_setc = np.array(gld_data['hvac']['cooling_setpoint']['values']).astype(np.float)
wh_tanks = np.array(gld_data['wh']['tank_setpoint']['values']).astype(np.float)

# Device Power Outputs
battInv_power = (np.array(gld_data['battInv']['power']['values'])).astype(np.cfloat)
solarInv_power = (np.array(gld_data['solarInv']['power']['values'])).astype(np.cfloat)
hvac_power = (np.array(gld_data['hvac']['power']['values'])).astype(np.cfloat)
wh_power = (np.array(gld_data['wh']['power']['values'])).astype(np.cfloat)
#aggregating device outputs per adc in adc_agg dict
# adc_agg['adc name']['der type']=sum of all devices of der type
t=time.time()
adc_agg = copy.deepcopy(adc_ind)
for adc_num in adc_ind:
    if "battInv" in adc_agg[adc_num]:
        adc_agg[adc_num]["battInv"] = np.sum(battInv_power[:, adc_ind[adc_num]['battInv']], 1)/1000
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["battInv"]
    if "solarInv" in adc_agg[adc_num]:
        adc_agg[adc_num]["solarInv"] = np.sum(solarInv_power[:, adc_ind[adc_num]['solarInv']], 1) / 1000
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["solarInv"]
    if "hvac" in adc_agg[adc_num]:
        adc_agg[adc_num]["hvac"] = np.sum(hvac_power[:, adc_ind[adc_num]['hvac']], 1)
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["hvac"]
    if "wh" in adc_agg[adc_num]:
        adc_agg[adc_num]["wh"] = np.sum(wh_power[:, adc_ind[adc_num]['wh']], 1)
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["wh"]
print('elapsed time is ',time.time()-t)

# #
# battInv_rated = (np.array(gld_data['battInv']['rated_power']['values'])).astype(np.float)
# batt_rated = (np.array(gld_data['batt']['rated_power']['values'])).astype(np.float)
# solar_rated = (np.array(gld_data['solar']['rated_power']['values'])).astype(np.float)

#Plot aggregate devices output at given adc for each der type
adc_num = '109'
hrs = np.arange(len(wh_power[:,0]))
fig1, ax1 = plt.subplots(2, 2, sharex='col')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['battInv']), label='Battery')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['solarInv']), label='Solar')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['wh']), label='WH')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['hvac']), label='HVAC')
ax1[0,0].set_ylabel("kW")
ax1[0,0].set_title("Aggregated kW at ADC "+adc_num+" by DER")
ax1[0,0].legend(loc='best')

ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['battInv']), label='Battery')
ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['solarInv']), label='Solar')
ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['wh']), label='WH')
ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['hvac']), label='HVAC')
ax1[0,1].set_ylabel("kVar")
ax1[0,1].set_title("Aggregated kVar at ADC "+adc_num+" by DER")
ax1[0,1].legend(loc='best')

ax1[1,0].plot(hrs, np.real(adc_agg[adc_num]['total']), label='ADC output')
ax1[1,0].step((PQ_opt['time']),np.array(PQ_opt[adc_num]['Popt']),'k', linestyle='--', where='post', label='ADC set point')
ax1[1,0].set_ylabel("kW")
ax1[1,0].set_title("Aggregated P at ADC "+adc_num)
ax1[1,0].legend(loc='best')

ax1[1,1].plot(hrs, np.imag(adc_agg[adc_num]['total']), label='ADC output')
ax1[1,1].step(PQ_opt['time'],np.array(PQ_opt[adc_num]['Qopt']),'k--', linestyle='--', where='post',label='ADC set point')
ax1[1,1].set_ylabel("kVar")
ax1[1,1].set_title("Aggregated Q at ADC "+adc_num)
ax1[1,1].legend(loc='best')
plt.show()

# #plot
# fig2, ax2 = plt.subplots()
#
# ax2.plot(hrs, )
# plt.figure(1)
# plt.plot(hrs,solarInv_Pout[:,3],label='Pout')
# plt.plot(hrs,solarInv_Qout[:,3],label='Qout')
# plt.plot(hrs,np.real(solarInv_power[:,3]),'--', label='VAout_real')
# plt.plot(hrs,np.imag(solarInv_power[:,3]),'--', label='VAout_var')
# # plt.plot(np.arange(168), solar_rated[0],'--',label='solar rating')
# plt.plot(hrs,np.abs(solarInv_power[:,3]),'k--',label='VAout_mag')
# plt.legend(loc='best')
#
# plt.figure(2)
# plt.plot(hrs, battInv_Pout[:,3], label='Pout')
# plt.plot(hrs, battInv_Qout[:,3], label='Qout')
# plt.plot(hrs, np.real(battInv_power[:,3]),'--', label='VAout_real')
# plt.plot(hrs, np.imag(battInv_power[:,3]),'--', label='VAout_var')
# # plt.plot(np.arange(505), batt_rated[0],'--',label='battery rating')
# # plt.plot(np.arange(505), battInv_rated[0],'--',label='battery inverter rating')
# plt.plot(hrs, np.abs(battInv_power[:,3]),'k--',label='VAout_mag')
# plt.legend(loc='best')
# plt.show()
