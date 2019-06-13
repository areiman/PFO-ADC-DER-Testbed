import numpy as np
import matplotlib.pyplot as plt
import copy

def calculate(adc_agg, adc_Prating, cosim_data):
    adc_err_kw = {}
    adc_err_kw["adc_num"] = []
    adc_err_kw["battInv"] = np.array([])
    adc_err_kw["solarInv"] = np.array([])
    adc_err_kw["hvac"] = np.array([])
    adc_err_kw["wh"] = np.array([])
    adc_err_kw["total"] = np.array([])
    adc_err_kw["solar_batt"] = np.array([])
    adc_err_pu = copy.deepcopy(adc_err_kw)
    total_rating_der = 0
    num_der = {}
    total_num_der = 0
    for adc_num in adc_agg:
        adc_err_kw["adc_num"].append(adc_num)
        if "battInv" in adc_agg[adc_num]:
            num_der[adc_num] = len(adc_agg[adc_num]['battInv'])
            temp_err_batt = cosim_data[adc_num]['Popt_BATT'][0:2] - np.real(adc_agg[adc_num]['battInv'])[3:6:2]
            adc_err_kw['battInv'] = np.append(adc_err_kw['battInv'], (np.sum(abs(temp_err_batt))/len(temp_err_batt)))
            adc_err_pu['battInv'] = np.append(adc_err_pu['battInv'],
                                              (np.sum(abs(temp_err_batt)) / len(temp_err_batt) / adc_Prating[adc_num]['battInv']))
            sol_batt = temp_err_batt
            sol_batt_rat = adc_Prating[adc_num]['battInv']
        else:
            adc_err_kw['battInv'] = np.append(adc_err_kw['battInv'], np.nan)
            adc_err_pu['battInv'] = np.append(adc_err_pu['battInv'],  np.nan)
            sol_batt = np.full(len(temp_err_batt), np.nan)
            sol_batt_rat = np.nan

        if "solarInv" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['solarInv'])
            temp_err_pv = (cosim_data[adc_num]['Popt_PV'][0:2] - np.real(adc_agg[adc_num]['solarInv'])[3:6:2])
            adc_err_kw['solarInv'] = np.append(adc_err_kw['solarInv'], (np.sum(abs(temp_err_pv))/len(temp_err_pv)))
            adc_err_pu['solarInv'] = np.append(adc_err_pu['solarInv'],
                                              (np.sum(abs(temp_err_pv)) / len(temp_err_pv) / adc_Prating[adc_num]['solarInv']))
            sol_batt = np.nansum([sol_batt, temp_err_pv],0)
            sol_batt_rat = np.nansum([adc_Prating[adc_num]['solarInv'], sol_batt_rat])
        else:
            adc_err_kw['solarInv'] = np.append(adc_err_kw['solarInv'], np.nan)
            adc_err_pu['solarInv'] = np.append(adc_err_pu['solarInv'], np.nan)
            sol_batt = np.nansum([sol_batt, np.full(len(temp_err_batt), np.nan)],0)
            sol_batt_rat = np.nansum([np.nan, sol_batt_rat])

        adc_err_kw['solar_batt'] = np.append(adc_err_kw["solar_batt"], sum(abs(sol_batt))/len(sol_batt))
        adc_err_pu['solar_batt'] = np.append(adc_err_pu["solar_batt"], sum(abs(sol_batt)) / len(sol_batt) / sol_batt_rat)

        if "hvac" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['hvac'])
            temp_err = (cosim_data[adc_num]['Popt_HVAC'][0:2] - np.real(adc_agg[adc_num]['hvac'])[3:6:2])
            adc_err_kw['hvac'] = np.append(adc_err_kw['hvac'], (np.sum(abs(temp_err))/len(temp_err)))
            adc_err_pu['hvac'] = np.append(adc_err_pu['hvac'],
                                              (np.sum(abs(temp_err)) / len(temp_err) / adc_Prating[adc_num]['hvac']))
        else:
            adc_err_kw['hvac'] = np.append(adc_err_kw['hvac'], np.nan)
            adc_err_pu['hvac'] = np.append(adc_err_pu['hvac'], np.nan)

        if "wh" in adc_agg[adc_num]:
            num_der[adc_num] = num_der[adc_num] + len(adc_agg[adc_num]['wh'])
            temp_err = (cosim_data[adc_num]['Popt_WH'][0:2] - np.real(adc_agg[adc_num]['wh'])[3:6:2])
            adc_err_kw['wh'] = np.append(adc_err_kw['wh'], (np.sum(abs(temp_err))/len(temp_err)))
            adc_err_pu['wh'] = np.append(adc_err_pu['wh'],
                                              (np.sum(abs(temp_err)) / len(temp_err) / adc_Prating[adc_num]['wh']))
        else:
            adc_err_kw['wh'] = np.append(adc_err_kw['wh'], np.nan)
            adc_err_pu['wh'] = np.append(adc_err_pu['wh'], np.nan)

        temp_err = (cosim_data[adc_num]['Popt'][0:2] - np.real(adc_agg[adc_num]['total'])[3:6:2])
        adc_err_kw['total'] = np.append(adc_err_kw['total'], (np.sum(abs(temp_err))/len(temp_err)))
        adc_err_pu['total'] = np.append(adc_err_pu['total'],
                                        (np.sum(abs(temp_err)) / len(temp_err)) / adc_Prating[adc_num]['total'])
        total_num_der = total_num_der + num_der[adc_num]
        total_rating_der = total_rating_der + adc_Prating[adc_num]['total']

    # print('avergae P mismatch index is ', np.mean(adc_err_kw['total']), 'kW per ADC')
    # print('avergae P mismatch index is ', np.mean(adc_err_pu['total']), 'pu per ADC')
    # print('average total DER rating is ', total_rating_der/len(adc_agg), 'kW per ADC')
    print('--------------------------------------------')
    print('Net P mismatch index:  ', "{0:.2f}".format(np.nanmean(adc_err_kw['total'])), 'kW     and     ',
          "{0:.2f}".format(np.nanmean(adc_err_pu['total'])), 'pu per ADC')
    print('Individual Control Performance:')
    print('     solar:    ', "{0:.2f}".format(np.nanmean(adc_err_kw['solarInv']))  , 'kW     |', "{0:.2f}".format(np.nanmean(adc_err_pu['solarInv'])), 'pu per ADC')
    print('     battery:  ', "{0:.2f}".format(np.nanmean(adc_err_kw['battInv']))   , 'kW     |', "{0:.2f}".format(np.nanmean(adc_err_pu['battInv'])), 'pu per ADC')
    print('     pv+batt:  ', "{0:.2f}".format(np.nanmean(adc_err_kw['solar_batt'])), 'kW     |', "{0:.2f}".format(np.nanmean(adc_err_pu['solar_batt'])), 'pu per ADC')
    print('     HVAC:     ', "{0:.2f}".format(np.nanmean(adc_err_kw['hvac']))      , 'kW     |', "{0:.2f}".format(np.nanmean(adc_err_pu['hvac'])), 'pu per ADC')
    print('     WH:       ', "{0:.2f}".format(np.nanmean(adc_err_kw['wh']))        , 'kW     |', "{0:.2f}".format(np.nanmean(adc_err_pu['wh'])), 'pu per ADC')

    fig4, ax4 = plt.subplots(2, 2)
    # ax4[0, 0].plot(adc_err_kw['adc_num'],adc_err_kw['battInv'], label='Battery')
    # ax4[0, 0].plot(adc_err_kw['solarInv'], label='Solar')
    ax4[0, 0].plot(adc_err_kw['adc_num'], adc_err_kw['solar_batt'], label='Solar+Batt') # solar + battery
    ax4[0, 0].plot(adc_err_kw['wh'], label='WH')
    ax4[0, 0].plot(adc_err_kw['hvac'], label='HVAC')
    ax4[0, 0].plot(adc_err_kw['total'], 'k', label='Net')
    ax4[0, 0].set_ylabel("kW")
    ax4[0, 0].set_xlabel("ADC number")
    ax4[0, 0].set_title("P mismatch (kW) at all ADCs")
    ax4[0, 0].legend(loc='best')

    # ax4[0, 1].plot(adc_err_kw['adc_num'], adc_err_pu['battInv'], label='Battery')
    # ax4[0, 1].plot(adc_err_pu['solarInv'], label='Solar')
    ax4[0, 1].plot(adc_err_kw['adc_num'], adc_err_pu['solar_batt'], label='Solar+Batt')  # solar + battery
    ax4[0, 1].plot(adc_err_pu['wh'], label='WH')
    ax4[0, 1].plot(adc_err_pu['hvac'], label='HVAC')
    ax4[0, 1].plot(adc_err_pu['total'], 'k', label='Net')
    ax4[0, 1].set_ylabel("pu")
    ax4[0, 1].set_xlabel("ADC number")
    ax4[0, 1].set_title("P mismatch (pu) at all ADCs")
    ax4[0, 1].legend(loc='best')

    # plt.show()
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
