import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv
import time
import copy
import os
from datetime import datetime
import error_metrics

global gld_num
gld_num = '1'
os.chdir('/home/ankit/PFO-ADC-DER-Testbed/ADC-DER-Testbed/testbed/post_process')
# discard_time = 3600*4
## loading cosim_manager data
lp = open('./cosim_data.json').read()
cosim_data = json.loads(lp)
## Appending all cosim data with one more entry
for key, value in cosim_data.items():
    for k, v in value.items():
        if k == 'Timestamp':
            # v.append(v[-1]+v[-1]-v[-2]) # adding one more timestamp
            v.append(v[-1] + v[0])
        else:
            v.append(v[-1]) # repeating the last value again
        cosim_data[key][k] = v
cosim_time = cosim_data[list(cosim_data)[0]]['Timestamp']
cosim_data['time'] = np.array([int(i) for i in cosim_time])

# create mapping of each node to its ADC
adc_nodes_map=[]
adc_file = "./../../../GLD/initial_scenario/ADC_Location/ADC_Placement_by_Voltage_Drop.csv"
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
    adc_name = 'M' + gld_num + '_ADC' + adc_nodes_map[ind,1]
    return adc_name

# Loading gld_data.json
lp = open('GLD_' + gld_num + '_data.json').read()
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
        if find_adc(b) == 'M1_ADCNONE':
            continue
        if find_adc(b) not in adc_ind:
            adc_ind[find_adc(b)] = {}
        if der[0] not in adc_ind[find_adc(b)]:
            adc_ind[find_adc(b)][der[0]]=[]
        adc_ind[find_adc(b)][der[0]].append(obj.index(a))
# print('elapsed time is ',time.time()-t)

#Voltages
voltages = np.array(gld_data['hvac']['voltages']['values']).astype(np.cfloat)
# Actuation Signals
#hrs = gld_data['battInv']['P_Out']['time']
battInv_Pout = np.array(gld_data['battInv']['P_Out']['values']).astype(np.float)
battInv_Qout = np.array(gld_data['battInv']['Q_Out']['values']).astype(np.float)
solarInv_Pout = np.array(gld_data['solarInv']['P_Out']['values']).astype(np.float)
solarInv_Qout = np.array(gld_data['solarInv']['Q_Out']['values']).astype(np.float)
hvac_seth = np.array(gld_data['hvac']['heating_setpoint']['values']).astype(np.float)
hvac_setc = np.array(gld_data['hvac']['cooling_setpoint']['values']).astype(np.float)
hvac_cooling_demand = (np.array(gld_data['hvac']['cooling_demand']['values'])).astype(np.float)
hvac_fan_power = (np.array(gld_data['hvac']['fan_design_power']['values'])).astype(np.float)/1000
hvac_rating = hvac_cooling_demand+hvac_fan_power
hvac_c_thermal_capacity = (np.array(gld_data['hvac']['design_cooling_capacity']['values'])).astype(np.float)
hvac_c_cop = (np.array(gld_data['hvac']['cooling_COP']['values'])).astype(np.float)
hvac_rating1 = hvac_c_thermal_capacity/12000/hvac_c_cop*3.5168
wh_tanks = np.array(gld_data['wh']['tank_setpoint']['values']).astype(np.float)
hvac_c_status = np.array(gld_data['hvac']['cooling_status']['values']).astype(np.float)
wh_rating = np.array(gld_data['wh']['heating_element_capacity']['values']).astype(np.float)
battInv_rated = (np.array(gld_data['battInv']['rated_power']['values'])).astype(np.float)
batt_rated = (np.array(gld_data['batt']['rated_power']['values'])).astype(np.float)
solar_rated = (np.array(gld_data['solar']['rated_power']['values'])).astype(np.float)

# Device Power Outputs
battInv_power = (np.array(gld_data['battInv']['power']['values'])).astype(np.cfloat)
solarInv_power = (np.array(gld_data['solarInv']['power']['values'])).astype(np.cfloat)
hvac_power = (np.array(gld_data['hvac']['power']['values'])).astype(np.cfloat)
wh_power = (np.array(gld_data['wh']['power']['values'])).astype(np.cfloat)

solar_VA = (np.array(gld_data['solar']['VA']['values'])).astype(np.cfloat)
#aggregating device outputs per adc in adc_agg dict
# adc_agg['adc name']['der type']=sum of all devices of der type
t=time.time()
adc_agg = copy.deepcopy(adc_ind)
adc_Prating = {}
num_der = {}
total_num_der = 0
for adc_num in adc_ind:
    adc_Prating[adc_num] = {}
    if "battInv" in adc_agg[adc_num]:
        adc_agg[adc_num]["battInv"] = np.sum(battInv_power[:, adc_ind[adc_num]['battInv']], 1)/1000
        adc_agg[adc_num]["batt_Pout"] = np.sum(battInv_Pout[:, adc_ind[adc_num]['battInv']], 1) / 1000
        adc_agg[adc_num]["batt_Qout"] = np.sum(battInv_Qout[:, adc_ind[adc_num]['battInv']], 1) / 1000
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["battInv"]
        adc_Prating[adc_num]["battInv"] = np.sum(battInv_rated[0, adc_ind[adc_num]['battInv']])/1000
        adc_Prating[adc_num]["total"] = adc_Prating[adc_num]["battInv"]
    if "solarInv" in adc_agg[adc_num]:
        adc_agg[adc_num]["solarInv"] = np.sum(solarInv_power[:, adc_ind[adc_num]['solarInv']], 1) / 1000
        adc_agg[adc_num]["solar_Pout"] = np.sum(solarInv_Pout[:, adc_ind[adc_num]['solarInv']], 1) / 1000
        adc_agg[adc_num]["solar_Qout"] = np.sum(solarInv_Qout[:, adc_ind[adc_num]['solarInv']], 1) / 1000
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["solarInv"]
        adc_Prating[adc_num]["solarInv"] = np.sum(solar_rated[0, adc_ind[adc_num]['solarInv']]) / 1000
        adc_Prating[adc_num]["solarVA"] = np.sum(solar_VA[:, adc_ind[adc_num]['solarInv']], 1) / 1000
        adc_Prating[adc_num]["total"] = adc_Prating[adc_num]["total"] + adc_Prating[adc_num]["solarInv"]
    if "hvac" in adc_agg[adc_num]:
        adc_agg[adc_num]["hvac"] = np.sum(hvac_power[:, adc_ind[adc_num]['hvac']], 1)
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["hvac"]
        adc_Prating[adc_num]["hvac"] = np.sum(hvac_rating[0, adc_ind[adc_num]['hvac']])
        adc_Prating[adc_num]["total"] = adc_Prating[adc_num]["total"] + adc_Prating[adc_num]["hvac"]
    if "wh" in adc_agg[adc_num]:
        adc_agg[adc_num]["wh"] = np.sum(wh_power[:, adc_ind[adc_num]['wh']], 1)
        adc_agg[adc_num]["total"] = adc_agg[adc_num]["total"] + adc_agg[adc_num]["wh"]
        adc_Prating[adc_num]["wh"] = np.sum(wh_rating[0, adc_ind[adc_num]['wh']])
        adc_Prating[adc_num]["total"] = adc_Prating[adc_num]["total"] + adc_Prating[adc_num]["wh"]

error_metrics.calculate(adc_agg, adc_Prating, cosim_data)

#Plot aggregate devices output at given adc for each der type
time_format = '%H:%M:%S'
time_stamp = [t.split(' ')[1] for t in gld_data['wh']['power']['time']]
time_h = [datetime.strptime(t, '%H:%M:%S') for t in time_stamp]
hrs = [int((i-time_h[0]).total_seconds()) for i in time_h]
# start_time = 3600*4
adc_num = 'M1_ADC18'
# total_rating = sum(wh_rating[0, adc_ind[adc_num]['wh']]) + sum(hvac_rating[0, adc_ind[adc_num]['hvac']]) + sum(
#     battInv_rated[0, adc_ind[adc_num]['battInv']]) / 1000 + sum(solar_rated[0, adc_ind[adc_num]['solarInv']]) / 1000
fig1, ax1 = plt.subplots(2, 2, sharex='col')
# ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['batt_Pout']), label='Battery', color='C0')
# ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['solar_Pout']), label='Solar', color='C1')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['batt_Pout'] + adc_agg[adc_num]['solar_Pout']), label='Solar+Battery', color='C2')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['wh']), label='WH', color='C3')
ax1[0,0].plot(hrs, np.real(adc_agg[adc_num]['hvac']), label='HVAC', color='C4')
#
# ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_BATT'])/1,'k', linestyle='--', color='C0', where='post', label='battery set point')
# ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_PV'])/1,'k', linestyle='--', color='C1',  where='post', label='pv set point')
ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_PV']) + np.array(cosim_data[adc_num]['Popt_BATT']),'k', linestyle='--', color='C2',  where='post', label='PV+Batt set point')
ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_WH'])/1,'k', linestyle='--', color='C3', where='post', label='WH set point')
ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_HVAC'])/1,'k', linestyle='--', color='C4', where='post', label='AC set point')
ax1[0,0].set_ylabel("kW")
ax1[0,0].set_title("Aggregated kW at ADC "+adc_num+" by DER")
ax1[0,0].legend(loc='best')
# plt.xlim(left=start_time)

# ax1[0,1].plot(hrs, np.real(adc_agg[adc_num]['batt_Qout']), label='Battery')
# ax1[0,1].plot(hrs, np.real(adc_agg[adc_num]['solar_Qout']), label='Solar')
ax1[0,1].plot(hrs, np.real(adc_agg[adc_num]['batt_Qout'] + adc_agg[adc_num]['solar_Qout']), label='Solar+Battery', color='C2')
ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['wh']), label='WH', color='C3')
ax1[0,1].plot(hrs, np.imag(adc_agg[adc_num]['hvac']), label='HVAC', color='C4')

# ax1[0,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_BATT'])/1,'k', linestyle='--', color='C0', where='post', label='battery set point')
# ax1[0,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_PV'])/1,'k', linestyle='--', color='C1', where='post', label='pv set point')
ax1[0,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_PV']) + np.array(cosim_data[adc_num]['Qopt_BATT']),'k', linestyle='--', color='C2',  where='post', label='PV+Batt set point')
ax1[0,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_WH'])/1,'k', linestyle='--', color='C3', where='post', label='WH set point')
ax1[0,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_HVAC'])/1,'k', linestyle='--', color='C4', where='post', label='AC set point')

ax1[0,1].set_ylabel("kVar")
ax1[0,1].set_title("Aggregated kVar at ADC "+adc_num+" by DER")
ax1[0,1].legend(loc='best')
# plt.xlim(left=start_time)

ax1[1,0].plot(hrs, np.real(adc_agg[adc_num]['total']), label='ADC output')
ax1[1,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt']),'k', linestyle='--', where='post', label='ADC P*')
ax1[1,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt'])-np.array(cosim_data[adc_num][' Popt_unserved']),'r', linestyle='--', where='post', label='ADC servable setpoint')
ax1[1,0].set_ylabel("kW")
ax1[1,0].set_title("Aggregated P at ADC "+adc_num)
ax1[1,0].legend(loc='best')
# plt.xlim(left=start_time)

ax1[1,1].plot(hrs, np.imag(adc_agg[adc_num]['total']), label='ADC output')
ax1[1,1].step(cosim_data['time'],np.array(cosim_data[adc_num]['Qopt'])/1,'k--', linestyle='--', where='post',label='ADC set point')
ax1[1,1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt'])-np.array(cosim_data[adc_num][' Qopt_unserved']),'r', linestyle='--', where='post', label='ADC servable setpoint')
ax1[1,1].set_ylabel("kVar")
ax1[1,1].set_title("Aggregated Q at ADC "+adc_num)
ax1[1,1].legend(loc='best')
# plt.xlim(left=start_time)
plt.show()
cool_on_ind = np.nonzero(hvac_c_status[-1,:])[0]
# fig2, ax2 = plt.subplots(2, 2, sharex='col')
# # ax2.plot(hrs, np.abs(voltages[:,adc_ind[adc_num]['hvac']])/120
# ax2[1,0].plot(np.abs(voltages[-1,cool_on_ind])/120)
# ax2[1,0].plot(np.ones(len(cool_on_ind), int), 'r--')
# ax2[1,0].set_title("Voltages at all residential meters")
# ax2[1,0].set_ylabel("pu")
# ax2[1,0].set_xlabel("individual devices")
#
# # ax3.plot(hvac_rating[-1,cool_on_ind],linestyle='None', marker = 'o', markersize=2, label='rating')
# # ax3.plot(np.real(hvac_power[-1,cool_on_ind]),linestyle='None', marker = 'o', markersize=2, label='Output')
# ax2[0,0].plot(hvac_rating[-1,cool_on_ind]- np.real(hvac_power[-1,cool_on_ind]), label='rating-output')
# ax2[0,0].set_title("Difference between HVAC Rating and Output (Rating - Output)")
# ax2[0,0].set_ylabel("kW")
# ax2[0,0].set_xlabel("individual devices")
# ax2[0,0].legend(loc='best')
#
# ax2[0,1].plot((hvac_rating[-1,cool_on_ind]- np.real(hvac_power[-1,cool_on_ind]))/hvac_rating[-1,cool_on_ind] *100, label='(rating-output)/rating*100')
# ax2[0,1].set_title("% Error between HVAC Rating and Output (Rating - Output)/Rating")
# ax2[0,1].set_ylabel("%")
# ax2[0,1].set_xlabel("individual devices")
# ax2[0,1].legend(loc='best')
#
# ax2[1,1].plot(np.imag(hvac_power[-1,cool_on_ind])/np.real(hvac_power[-1,cool_on_ind]))
# ax2[1,1].set_title("Q/P")
# ax2[1,1].set_ylabel("ratio")
# ax2[1,1].set_xlabel("individual devices")
# ax2[1,1].legend(loc='best')

# # plt.show()
# # #plot
# fig3, ax3 = plt.subplots()
# plt.figure(1)
# pv_ind = 10
# plt.plot(hrs,solarInv_Pout[:,pv_ind],label='P_set', color='C1')
# plt.plot(hrs,solarInv_Qout[:,pv_ind],label='Q_set', color='C2')
# plt.plot(hrs,np.abs(solarInv_Pout[:,pv_ind] + 1j*solarInv_Qout[:,pv_ind]),label='VA_set', color='C3')
# plt.plot(hrs,np.real(solarInv_power[:,pv_ind]),'--', label='P_actual', color='C1')
# plt.plot(hrs,np.imag(solarInv_power[:,pv_ind]),'--', label='Q_actual', color='C2')
# plt.plot(hrs,np.abs(solarInv_power[:,pv_ind]),'k--',label='VA_actual', color='C3')
# plt.plot(hrs, np.ones(len(hrs))*solar_rated[0,pv_ind], '--',label='solar rating', color='k')
# plt.legend(loc='best')
#
# fig4, ax4 = plt.subplots()
# time_ind = 400
# plt.plot(np.arange(168),solarInv_Pout[time_ind,:],label='P_set', color='C1')
# plt.plot(np.arange(168),solarInv_Qout[time_ind,:],label='Q_set', color='C2')
# plt.plot(np.arange(168),np.abs(solarInv_Pout[time_ind,:] + 1j*solarInv_Qout[time_ind,:]),label='VA_set', color='C3')
# plt.plot(np.arange(168),np.real(solarInv_power[time_ind,:]),'--', label='P_actual', color='C1')
# plt.plot(np.arange(168),np.imag(solarInv_power[time_ind,:]),'--', label='Q_actual', color='C2')
# plt.plot(np.arange(168), np.abs(solarInv_power[time_ind,:]),'k--',label='VA_actual', color='C3')
# plt.plot(np.arange(168), solar_rated[0],'--',label='solar rating', color='k')
# plt.plot(np.arange(168), np.abs(solar_VA[time_ind,:]),'--',label='PV_max')
# plt.legend(loc='best')
#
# #
# plt.figure(8)
# # plt.plot(hrs, battInv_Pout[:,3], label='Pout', color='C1')
# # plt.plot(hrs, battInv_Qout[:,3], label='Qout', color='C2')
# # plt.plot(hrs,np.abs(battInv_Pout[:,3] + 1j*battInv_Qout[:,3]),label='VA_set', color='C3')
# # plt.plot(hrs, np.real(battInv_power[:,3]),'--', label='P_actual', color='C1')
# # plt.plot(hrs, np.imag(battInv_power[:,3]),'--', label='Q_actual', color='C2')
# plt.plot(np.arange(505), batt_rated[0],'--',label='battery rating')
# plt.plot(np.arange(505), battInv_rated[0],'--',label='battery inverter rating')
# plt.plot(np.arange(505), battInv_Pout[400,:],'--',label='battery P_out')
# plt.plot(np.arange(505), np.real(battInv_power[400,:]),'--', label='P_actual')
# # plt.plot(hrs, np.abs(battInv_power[:,3]),'k--',label='VA_actual', color='C3')
# plt.legend(loc='best')
#
# plt.figure(9)
# out_temp = (np.array(gld_data['hvac']['outside_temperatrue']['values'])).astype(np.float)
# inside_temp = (np.array(gld_data['hvac']['air_temperature']['values'])).astype(np.float)
# plt.plot(hrs, inside_temp[:,adc_ind[adc_num ]['hvac']])
# plt.plot(hrs, hvac_setc[:,adc_ind[adc_num]['hvac']])
# # plt.plot(out_temp)

# *** Plotting bid curves *****
# fig2, ax2
# ax1[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_PV']) + np.array(cosim_data[adc_num]['Popt_BATT']),'k', linestyle='--', color='C2',  where='post', label='PV+Batt set point')

#----------------------------------------------------
## ------ Validation of AC Controller ---------------
#----------------------------------------------------
# fig2, ax2 = plt.subplots(2,2, sharex='col')
# out_temp = (np.array(gld_data['hvac']['outside_temperatrue']['values'])).astype(np.float)
# inside_temp = (np.array(gld_data['hvac']['air_temperature']['values'])).astype(np.float)
#
# ax2[0,0].plot(hrs, np.real(adc_agg[adc_num]['hvac']), label='HVAC', color='C4')
# ax2[0,0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_HVAC'])/1,'k', linestyle='--', color='C4', where='post', label='AC set point')
# ax2[0,0].set_ylabel("kW")
# ax2[0,0].set_title("Aggregated kW at ADC "+adc_num+" by DER")
# ax2[0,0].legend(loc='best')
#
# ax2[1,1].plot(hrs, inside_temp[:,adc_ind[adc_num ]['hvac']])
# ax2[1,1].set_title("Inside Temperature")
# ax2[1,1].set_ylabel("degree F")
# ax2[1,1].set_xlabel("Time (Seconds")
#
# ax2[0,1].plot(hrs, hvac_setc[:,adc_ind[adc_num]['hvac']])
# ax2[0,1].set_title("Cooling setpoint")
# ax2[0,1].set_ylabel("degree F")
# ax2[0,1].set_xlabel("Time (Seconds")
# # ax2[0].plot(out_temp)

# # ax2[1].plot(hrs, hvac_c_status[:,adc_ind[adc_num]['hvac']])
# ax2[1,0].plot(hrs,np.count_nonzero(hvac_c_status[:,adc_ind[adc_num]['hvac']], 1))
# ax2[1,0].set_title("Total number of ON AC-devices")
# ax2[1,0].set_ylabel("#")
# ax2[1,0].set_xlabel("Time (Seconds")
#
plt.show()

## ***** Feasibility check plot for solar PV and Battery ***********
# plt.rc('text', usetex=True)
fig3, ax3 = plt.subplots(2, 2, sharex='col')
P_max_av = np.sqrt(np.square(np.ones(len(cosim_data['time']))*adc_Prating[adc_num]['solarInv'])- np.square(abs(np.array(cosim_data[adc_num]['Qopt_PV']))))
ax3[0,0].plot(hrs, np.ones(len(hrs))*(adc_Prating[adc_num]['solarInv']), label='P_inv_max', color='C2')
ax3[0,0].plot(hrs, np.real(adc_Prating[adc_num]['solarVA']), label='PV_solar_max', color='C3')
ax3[0,0].step((cosim_data['time']), P_max_av, label='P_avail@Q*', color='C4', where='post')
ax3[0,0].step((cosim_data['time']),abs(np.array(cosim_data[adc_num]['Popt_PV'])),'k', linestyle='--', color='C1',  where='post', label='P*_PV')
ax3[0,0].set_title("Solar P(kW) set-point feasibility for ADC "+adc_num)
ax3[0,0].set_ylabel("kW")
ax3[0,0].legend(loc='best')
# plt.xlim(left=start_time)

Q_min_av = np.sqrt(np.square(np.ones(len(hrs))*adc_Prating[adc_num]['solarInv'])- np.square(np.real(adc_Prating[adc_num]['solarVA'])))
Q_max_av = np.sqrt(np.square(np.ones(len(cosim_data['time']))*adc_Prating[adc_num]['solarInv'])- np.square(abs(np.array(cosim_data[adc_num]['Popt_PV']))))
ax3[0,1].plot(hrs, np.ones(len(hrs))*(adc_Prating[adc_num]['solarInv']), label='Q_inv_max', color='C2')
ax3[0,1].step((cosim_data['time']), Q_max_av, label='Q_avail@P*', color='C4', where='post')
ax3[0,1].step((cosim_data['time']),abs(np.array(cosim_data[adc_num]['Qopt_PV'])),'k', linestyle='--', color='C1',  where='post', label='Q*_PV')
ax3[0,1].set_title("Solar Q(kVar) set-point feasibility for ADC "+adc_num)
ax3[0,1].set_ylabel("kVar")
ax3[0,1].legend(loc='best')
# plt.xlim(left=start_time)

temp = (np.square(np.ones(len(cosim_data['time']))*adc_Prating[adc_num]['battInv'])- np.square(abs(np.array(cosim_data[adc_num]['Qopt_BATT']))))
for ind in range(len(temp)):
    if np.abs(temp[ind]) < 1e-8:
        temp[ind] = 0
Pbatt_max_av = np.sqrt(temp)
ax3[1,0].plot(hrs, np.ones(len(hrs))*(adc_Prating[adc_num]['battInv']), label='P_inv_max', color='C2')
ax3[1,0].step((cosim_data['time']), Pbatt_max_av, label='P_avail@Q*', color='C4', where='post')
ax3[1,0].step((cosim_data['time']),abs(np.array(cosim_data[adc_num]['Popt_BATT'])),'k', linestyle='--', color='C1',  where='post', label='P*_BATT')
ax3[1,0].set_title("Battery P(kW) set-point feasibility for ADC "+adc_num)
ax3[1,0].set_ylabel("kW")
ax3[1,0].set_xlabel("Time (sec)")
ax3[1,0].legend(loc='best')
# plt.xlim(left=start_time)

# Q_min_av = np.sqrt(np.square(np.ones(len(hrs))*adc_Prating[adc_num]['solarInv'])- np.square(np.real(adc_Prating[adc_num]['solarVA'])))
Qbatt_max_av = np.sqrt(np.square(np.ones(len(cosim_data['time']))*adc_Prating[adc_num]['battInv'])- np.square(abs(np.array(cosim_data[adc_num]['Popt_BATT']))))
ax3[1,1].plot(hrs, np.ones(len(hrs))*(adc_Prating[adc_num]['battInv']), label='Q_inv_max', color='C2')
ax3[1,1].step((cosim_data['time']), Qbatt_max_av, label='Q_avail@P*', color='C4', where='post')
ax3[1,1].step((cosim_data['time']),abs(np.array(cosim_data[adc_num]['Qopt_BATT'])),'k', linestyle='--', color='C1',  where='post', label='Q*_BATT')
ax3[1,1].set_title("Battery Q(kVar) set-point feasibility for ADC "+adc_num)
ax3[1,1].set_ylabel("kVar")
ax3[1,1].set_xlabel("Time (sec)")
ax3[1,1].legend(loc='best')
# plt.xlim(left=start_time)

#TODO: plot battery state of charge
## ***** Feasibility check plot for solar PV and Battery ***********

## ***** Validation for Solar PV and Battery Control *************
fig4, ax4 = plt.subplots(2, 1)
ax4[0].step((cosim_data['time']),np.array(cosim_data[adc_num]['Popt_PV']) + np.array(cosim_data[adc_num]['Popt_BATT']),'k', color='C1',  where='post', label='P*_PV_Batt')
ax4[0].plot(hrs, np.real(adc_agg[adc_num]['batt_Pout'] + adc_agg[adc_num]['solar_Pout']), label='P_set_PV_Batt', color='C2', linestyle='--')
ax4[0].set_ylabel("kW")
ax4[0].set_title("Combined Performance of PV+Batt P at ADC "+adc_num)
ax4[0].legend(loc='best')

ax4[1].step((cosim_data['time']),np.array(cosim_data[adc_num]['Qopt_PV']) + np.array(cosim_data[adc_num]['Qopt_BATT']),'k', color='C1',  where='post', label='Q*_PV_Batt')
ax4[1].plot(hrs, np.real(adc_agg[adc_num]['batt_Qout'] + adc_agg[adc_num]['solar_Qout']), label='Q_set_PV_Batt', color='C2', linestyle='--')
ax4[1].set_ylabel("kVar")
ax4[1].set_title("Combined Performance of PV+Batt Q at ADC "+adc_num)
ax4[1].legend(loc='best')

fig5, ax5 = plt.subplots(2, 2, sharex='col')
ax5[0,0].plot(hrs, np.real(adc_agg[adc_num]['solar_Pout']), label='P_set_PV', color='C2')
ax5[0,0].plot(hrs, np.real(adc_agg[adc_num]['solarInv']), label='P_actual_PV', color='C6', linestyle='--')
ax5[0,0].set_ylabel("kW")
ax5[0,0].set_title("Solar P output at ADC "+adc_num)
ax5[0,0].legend(loc='best')

ax5[0,1].plot(hrs, np.real(adc_agg[adc_num]['solar_Qout']), label='Q_set_PV', color='C2')
ax5[0,1].plot(hrs, np.imag(adc_agg[adc_num]['solarInv']), label='Q_actual_PV', color='C6', linestyle='--' )
ax5[0,1].set_ylabel("kVar")
ax5[0,1].set_title("Solar Q output at ADC "+adc_num)
ax5[0,1].legend(loc='best')

ax5[1,0].plot(hrs, np.real(adc_agg[adc_num]['batt_Pout']), label='P_set_BATT', color='C2')
ax5[1,0].plot(hrs, np.real(adc_agg[adc_num]['battInv']), label='P_actual_PV', color='C6', linestyle='--')
ax5[1,0].set_ylabel("kW")
ax5[1,0].set_title("Battery P output at ADC "+adc_num)
ax5[1,0].legend(loc='best')
ax5[1,0].set_xlabel("Time (sec)")

ax5[1,1].plot(hrs, np.real(adc_agg[adc_num]['batt_Qout']), label='Q_set_BATT', color='C2')
ax5[1,1].plot(hrs, np.imag(adc_agg[adc_num]['battInv']), label='Q_actual_BATT', color='C6', linestyle='--')
ax5[1,1].set_ylabel("kVar")
ax5[1,1].set_title("Battery Q output at ADC "+adc_num)
ax5[1,1].legend(loc='best')
ax5[1,1].set_xlabel("Time (sec)")

plt.show()