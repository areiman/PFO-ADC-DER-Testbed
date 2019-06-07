import numpy as np
import matplotlib.pyplot as plt

def calculate(adc_agg, adc_Prating, cosim_data):
    adc_err_dict = {}
    adc_err_dict["adc_num"] = []
    adc_err_dict["battInv"] = np.array([])
    adc_err_dict["solarInv"] = np.array([])
    adc_err_dict["hvac"] = np.array([])
    adc_err_dict["wh"] = np.array([])
    adc_err_dict["total"] = np.array([])
    adc_err_2 = np.array([])
    total_err_time_vec = np.array([])
    num_der = {}
    total_num_der = 0
    for adc_num in adc_agg:
        adc_err_dict["adc_num"].append(adc_num)
        if "battInv" in adc_agg[adc_num]:
            num_der[adc_num] = len(adc_agg[adc_num]['battInv'])
            temp_err = abs(cosim_data[adc_num]['Popt_BATT'][0:2] - np.real(adc_agg[adc_num]['battInv'])[3:6:2])
            adc_err_dict['battInv'] = np.append(adc_err_dict['battInv'], (np.sum(temp_err)/len(temp_err)))
        else:
            adc_err_dict['battInv'] = np.append(adc_err_dict['battInv'], np.nan)

        if "solarInv" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['solarInv'])
            temp_err = abs(cosim_data[adc_num]['Popt_PV'][0:2] - np.real(adc_agg[adc_num]['solarInv'])[3:6:2])
            adc_err_dict['solarInv'] = np.append(adc_err_dict['solarInv'], (np.sum(temp_err)/len(temp_err)))
        else:
            adc_err_dict['solarInv'] = np.append(adc_err_dict['solarInv'], np.nan)

        if "hvac" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['hvac'])
            temp_err = abs(cosim_data[adc_num]['Popt_HVAC'][0:2] - np.real(adc_agg[adc_num]['hvac'])[3:6:2])
            adc_err_dict['hvac'] = np.append(adc_err_dict['hvac'], (np.sum(temp_err)/len(temp_err)))
        else:
            adc_err_dict['hvac'] = np.append(adc_err_dict['hvac'], np.nan)

        if "wh" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['wh'])
            temp_err = abs(cosim_data[adc_num]['Popt_WH'][0:2] - np.real(adc_agg[adc_num]['wh'])[3:6:2])
            adc_err_dict['wh'] = np.append(adc_err_dict['wh'], (np.sum(temp_err)/len(temp_err)))
        else:
            adc_err_dict['wh'] = np.append(adc_err_dict['wh'], np.nan)

        temp_err = abs(cosim_data[adc_num]['Popt'][0:2] - np.real(adc_agg[adc_num]['total'])[3:6:2])
        adc_err_dict['total'] = np.append(adc_err_dict['total'], (np.sum(temp_err)/len(temp_err)))
        adc_err_2 = np.append(adc_err_2, (np.sum(temp_err)/len(temp_err))/adc_Prating[adc_num]['total'])
        total_num_der = total_num_der + num_der[adc_num]

    avg_err = np.mean(adc_err_dict['total'])
    print('avergae P mismatch index is ', avg_err, 'kW per ADC')
    avg_err_2 = np.mean(adc_err_2)
    print('avergae P mismatch index is ', avg_err_2, 'pu per ADC')

    fig4, ax4 = plt.subplots(2, 2)
    ax4[0, 0].plot(adc_err_dict['adc_num'],adc_err_dict['battInv'], label='Battery')
    ax4[0, 0].plot(adc_err_dict['solarInv'], label='Solar')
    ax4[0, 0].plot(adc_err_dict['wh'], label='WH')
    ax4[0, 0].plot(adc_err_dict['hvac'], label='HVAC')
    ax4[0, 0].plot(adc_err_dict['total'], 'k', label='Net')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['batt_p']) / 1, 'k', linestyle='--', where='post',
    #                label='battery set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['pv_p']) / 1, 'k', linestyle='--', where='post',
    #                label='pv set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['ac_p']) / 1, 'k', linestyle='--', where='post',
    #                label='AC set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['ewh_p']) / 1, 'k', linestyle='--', where='post',
    #                label='WH set point')
    ax4[0, 0].set_ylabel("kW")
    ax4[0, 0].set_xlabel("ADC number")
    ax4[0, 0].set_title("P mismatch (kW) at all ADCs")
    ax4[0, 0].legend(loc='best')

    # ax4[1, 0].plot(adc_err_dict['adc_num'], adc_err_dict['battInv'], label='Battery')
    # ax4[0, 0].plot(adc_err_dict['solarInv'], label='Solar')
    # ax4[0, 0].plot(adc_err_dict['wh'], label='WH')
    # ax4[0, 0].plot(adc_err_dict['hvac'], label='HVAC')
    ax4[0, 1].plot(adc_err_2, 'k', label='Net')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['batt_p']) / 1, 'k', linestyle='--', where='post',
    #                label='battery set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['pv_p']) / 1, 'k', linestyle='--', where='post',
    #                label='pv set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['ac_p']) / 1, 'k', linestyle='--', where='post',
    #                label='AC set point')
    # ax1[0, 0].step((cosim_data['time']), np.array(cosim_data[adc_num]['ewh_p']) / 1, 'k', linestyle='--', where='post',
    #                label='WH set point')
    ax4[0, 1].set_ylabel("pu")
    ax4[0, 1].set_xlabel("ADC number")
    ax4[0, 1].set_title("P mismatch (pu) at all ADCs")
    ax4[0, 1].legend(loc='best')

    plt.show()
    #
    # getting the mistmatch error metric per adc as time vector
    # adc_err_time_vec[adc_num] = abs(cosim_data[adc_num]['Popt'][0:2] - np.real(adc_agg[adc_num]['total'])[3:6:2])
    # adc_err_time_vec[adc_num] = abs(cosim_data[adc_num]['Popt'][0:2] - np.real(adc_agg[adc_num]['total'])[3:6:2]) / \
    #                             cosim_data[adc_num]['Popt'][0:2]

    # if not total_err_time_vec.any():
    #     total_err_time_vec = adc_err_time_vec[adc_num]  # *num_der[adc_num]
    # total_err_time_vec = total_err_time_vec + adc_err_time_vec[adc_num]  # *num_der[adc_num]


# total_err_time_vec = total_err_time_vec  # /total_num_der
# avg_err_adc = total_err_time_vec / len(adc_ind)  # average error across adc (time vector)
# avg_err = sum(avg_err_adc) / len(avg_err_adc)  # average error across time (control signals)
# print('elapsed time is ', time.time() - t)
