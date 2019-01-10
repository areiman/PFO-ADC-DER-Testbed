%% ADC module
% Xinyang Zhou, Aug. 14, 2018

clc; clear; close all;

% Control time (minute)
deltat = 30;

% Number of PV-inverters and battery-inverters under control
n_pv = 10;
n_ba = 12;

%% PV inverter setup
% PV capacity; sampled from PV_params.csv
cap_pv = [4410.43 4480.22 4381.46 4462.06 4401.66 4439.82 4425.14 4429.96 4495.07 4506.36];
% % PV inverter efficiency; set to 100%
% eff_pv = ones(n_pv,1);
% Current available power, made up here
p_av = 4000 * ones(n_pv,1);


%% Battery setup
% Maximum charging/discharging power rates of battery-inverters; sampled from Battery_params.csv
p_ba_cha_max = -[1045.54	1050.14	1011.45	1040.56	1091.7	1041.74	1062.87	1056.41	1043.23	1009.26	1029.61	1034.23];
p_ba_dis_max =  [1045.54	1050.14	1011.45	1040.56	1091.7	1041.74	1062.87	1056.41	1043.23	1009.26	1029.61	1034.23];
% Capacity
cap_ba = [33778.1	27371.8	26543.3	35204.1	25158.3	23285.2	31995.7	28160.4	26867.4	30256.5	35692.9	29039];
% power ; depending on control time granularity; assume maximum power rate
% increase/decrease SOC by 10%
%power_SOC_rate = 0.1 * p_ba_dis_max;
% Battery inverter efficiency; set to 100%
eff_ba = ones(n_ba,1);
% Preferred SOC; uniformly set to 50%
SOC_set = 0.5 * ones(n_ba,1);
% Current SOC; uniformly set to 50%
SOC_now = 0.5 * ones(n_ba,1);

%% Optimal set point
% make up feasible values such that PV will curtail real power and inject 
% positive reactive power, and Batteries will charge
p_opt = 20000;
q_opt = 5000;

[p_pv, q_pv, p_ba] = ADC_control(deltat, n_pv, n_ba, cap_pv, p_av, ...
    cap_ba, p_ba_cha_max, p_ba_dis_max, eff_ba, SOC_set, SOC_now, p_opt, q_opt);
