import json
import numpy as np
import matplotlib as mpl;
import matplotlib.pyplot as plt;

lp = open('gld_data.json').read()
gld_data = json.loads(lp)

# Plot Actuation Signals
#hrs = gld_data['battInv']['P_Out']['time']
battInv_Pout = np.array(gld_data['battInv']['P_Out']['values']).astype(np.float)
battInv_Qout = np.array(gld_data['battInv']['Q_Out']['values']).astype(np.float)
battInv_VAout = (np.array(gld_data['battInv']['VA_Out']['values'])).astype(np.cfloat)
battInv_rated = (np.array(gld_data['battInv']['rated_power']['values'])).astype(np.float)
batt_rated = (np.array(gld_data['batt']['rated_power']['values'])).astype(np.float)
solarInv_Pout = np.array(gld_data['solarInv']['P_Out']['values']).astype(np.float)
solarInv_Qout = np.array(gld_data['solarInv']['Q_Out']['values']).astype(np.float)
solarInv_VAout = (np.array(gld_data['solarInv']['VA_Out']['values'])).astype(np.cfloat)
solar_rated = (np.array(gld_data['solar']['rated_power']['values'])).astype(np.float)
hvac_seth = np.array(gld_data['hvac']['heating_setpoint']['values']).astype(np.float)
hvac_setc = np.array(gld_data['hvac']['cooling_setpoint']['values']).astype(np.float)
wh_tanks = np.array(gld_data['wh']['tank_setpoint']['values']).astype(np.float)

adc={}
adc['battInv']={}
obj = gld_data['battInv']['P_Out']['object_name']
for a in obj:
    b = a.split('_')[-2][1:]
    #if 'l102_tm' in a:
    if b not in adc['battInv']:
        adc['battInv'][b]=[]
    adc['battInv'][b].append(obj.index(a))

adc['hvac']={}
obj = gld_data['hvac']['cooling_setpoint']['object_name']
for a in obj:
    b = a.split('_')[-2][1:]
    #if 'l102_tm' in a:
    if b not in adc['hvac']:
        adc['hvac'][b]=[]
    adc['hvac'][b].append(obj.index(a))

adc['wh']={}
obj = gld_data['wh']['tank_setpoint']['object_name']
for a in obj:
    b = a.split('_')[-2][1:]
    #if 'l102_tm' in a:
    if b not in adc['wh']:
        adc['wh'][b]=[]
    adc['wh'][b].append(obj.index(a))

adc['solarInv'] = {}
obj = gld_data['solarInv']['P_Out']['object_name']
for a in obj:
    b = a.split('_')[-2][1:]
    # if 'l102_tm' in a:
    if b not in adc['solarInv']:
        adc['solarInv'][b] = []
    adc['solarInv'][b].append(obj.index(a))

#fig1, ax1 = plt.subplots(1, 2, sharex='col')
plt.plot(np.arange(168),solarInv_Pout[3,:],label='Pout')
plt.plot(np.arange(168),solarInv_Qout[3,:],label='Qout')
plt.plot(np.arange(168),np.real(solarInv_VAout[3,:]),'--', label='VAout_real')
plt.plot(np.arange(168),np.imag(solarInv_VAout[3,:]),'--', label='VAout_var')
plt.plot(np.arange(168), solar_rated[0],'--',label='solar rating')
plt.plot(np.arange(168),np.abs(solarInv_VAout[3,:]),'k--',label='VAout_mag')
plt.legend(loc='best')
plt.show()

plt.plot(np.arange(505), battInv_Pout[3,:], label='Pout')
plt.plot(np.arange(505), battInv_Qout[3,:], label='Qout')
plt.plot(np.arange(505), np.real(battInv_VAout[3,:]),'--', label='VAout_real')
plt.plot(np.arange(505), np.imag(battInv_VAout[3,:]),'--', label='VAout_var')
plt.plot(np.arange(505), batt_rated[0],'--',label='battery rating')
plt.plot(np.arange(505), battInv_rated[0],'--',label='battery inverter rating')
plt.plot(np.arange(505), np.abs(battInv_VAout[3,:]),'k--',label='VAout_mag')
plt.legend(loc='best')
plt.show()

adc_num = '102'
hrs = np.arange(len(wh_tanks[:,0]))
fig1, ax1 = plt.subplots(2, 2, sharex='col')
ax1[0,0].plot(hrs, battInv_Pout[:,adc['battInv'][adc_num]], label='Pout')
ax1[0,0].plot(hrs, battInv_Qout[:,adc['battInv'][adc_num]], label='Qout')
ax1[0, 0].set_ylabel("Watt")
ax1[0, 0].set_title("Battery Inverter Power")
#ax1[0, 0].legend(loc='best')

ax1[0,1].plot(hrs, solarInv_Pout[:,adc['solarInv'][adc_num]], label='Pout')
ax1[0,1].plot(hrs, solarInv_Qout[:,adc['solarInv'][adc_num]], label='Qout')
ax1[0, 1].set_ylabel("Watt")
ax1[0, 1].set_title("Solar Inverter Power")
ax1[0, 1].legend(loc='best')

ax1[1,0].plot(hrs, wh_tanks[:,adc['wh'][adc_num]], label='wh_tank set point')
ax1[1,0].set_ylabel("degree F")
ax1[1,0].set_title("waterheater set point")
ax1[1,0].legend(loc='best')

ax1[1,1].plot(hrs, hvac_setc[:,adc['hvac'][adc_num]], label='hvac cooling set')
ax1[1,1].plot(hrs, hvac_seth[:,adc['hvac'][adc_num]], label='hvac heating set')
ax1[1,1].set_ylabel("degree F")
ax1[1,1].set_title("HVAC set points")
#ax1[1,1].legend(loc='best')

# ax1[0, 0].plot(hrs, hvac_load[hrs_start:], label="hvac")
# ax1[0, 0].plot(hrs, wh_load[hrs_start:], label="waterheater")
# ax1[0, 0].plot(hrs, total_load[hrs_start:] - hvac_load[hrs_start:], label="ZIP")
# ax1[0, 0].plot(hrs, total_load[hrs_start:], label="total")
# #ax1[0].plot(hrs, -inv_load, label="inverter")
# #ax1[0].plot(hrs, mtr_load, "k--", label="net meter",)
# #ax1[0].plot(hrs, total_load-inv_load, label="total+inv")
# ax1[0, 0].set_ylabel("kW")
# ax1[0, 0].set_title("Load Composition")
# ax1[0, 0].legend(loc='best')
plt.show()