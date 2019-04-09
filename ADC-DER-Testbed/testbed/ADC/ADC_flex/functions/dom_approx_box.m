function [F_adc,D_adc,wh_range,ac_range,pv_range,bat_range] = dom_approx_box(varargin)

syms p q d

disp('in dom_approx_box');

%% Input/Output specifications
% wh    : a structure of length equal to the number of electric water
% heaters, with fields "name" and "prated"
% ac    : a structure of length equal to the number of residential
% air-conditioners, with fields "name", "prated", "powfac"
% pv    : a structure of length equal to the number of solar photovoltaic
% inverters, with fields "name", "pgenmax", "invcap"
% bat   : a structure of length equal to the number of batteries, with
% fields "name", "prated", "invcap"
%
% (OPTIONAL) tools_dir: path to the SOS/SDP solvers
%
% F     : mx2 matrix, Fx <= D
% D     : mx1 vector
% wh_range  : 1x4 array of pmax,pmin,qmax,qmin of EWHs
% ac_range  : 1x4 array of pmax,pmin,qmax,qmin of ACs
% pv_range  : 1x4 array of pmax,pmin,qmax,qmin of PVs
% bat_range : 1x4 array of pmax,pmin,qmax,qmin of batteries

wh_pop  = varargin{1};
ac_pop  = varargin{2};
pv_pop  = varargin{3};
bat_pop = varargin{4};
if nargin>4
    addpath(genpath(varargin{5}))
end

%==========================================================
% Create a random population of devices
% Enter the type: battery, ewh, hvac, photovoltaic, wind
%==========================================================
p_step = 0.02; % [kW] this is the step-size used to discretize the p-axis
max_count = Inf;

wh_range = zeros(1,4);
ac_range = zeros(1,4);
pv_range = zeros(1,4);
bat_range = zeros(1,4);

dev_count = 0;

aggr_dev(1).params.prated = 0;      % EWH

aggr_dev(2).params.prated = 0;      % HVAC
aggr_dev(2).params.powfac = 0;      % HVAC

aggr_dev(3).params.pgenmax = 0;     % PV
aggr_dev(3).params.invcap = 0;      % PV

aggr_dev(4).params.prated = 0;      % battery
aggr_dev(4).params.invcap = 0;      % battery

for i = 1:length(wh_pop)
    dev_count = dev_count + 1;
    
    desc_of_dev(dev_count).type = 'ewh';
    [dev_constr,dev_conv_constr,dev_params] = wh_model(wh_pop(i));
    desc_of_dev(dev_count).constr       = dev_constr;
    desc_of_dev(dev_count).conv_constr  = dev_conv_constr;
    desc_of_dev(dev_count).params       = dev_params;
    
    pval = [];  % p-axis discretized in the feasible portion
    qmax = [];  % max q values at the discrete (feasible) p values
    qmin = [];  % min q values at the discrete (feasible) p values
    for j = 1:length(dev_constr)
        pval_temp = linspace(dev_constr{j}.prange(1),dev_constr{j}.prange(2),min(max_count,1+floor(diff(dev_constr{j}.prange)/p_step)));
        qmax_temp = double(subs(dev_constr{j}.qrange(2),p,pval_temp));
        qmin_temp = double(subs(dev_constr{j}.qrange(1),p,pval_temp));
        
        pval = [pval pval_temp];
        qmax = [qmax qmax_temp];
        qmin = [qmin qmin_temp];
    end
    
    desc_of_dev(dev_count).pval = pval;
    desc_of_dev(dev_count).qmax = qmax;
    desc_of_dev(dev_count).qmin = qmin;
    
    wh_range = wh_range + [max(pval) min(pval) max(qmax) min(qmin)];
end

aggr_dev(1).params.prated = wh_range(1);
[aggr_dev(1).constr,~,~] = wh_model(aggr_dev(1).params);

disp('done with wh')
for i = 1:length(ac_pop)
    dev_count = dev_count + 1;
    
    aggr_dev(2).params.prated = aggr_dev(2).params.prated + ac_pop(i).prated;
    aggr_dev(2).params.powfac = aggr_dev(2).params.powfac - (aggr_dev(2).params.powfac-ac_pop(i).powfac)*ac_pop(i).prated/aggr_dev(2).params.prated;
    
    desc_of_dev(dev_count).type = 'hvac';
    [dev_constr,dev_conv_constr,dev_params] = ac_model(ac_pop(i));
    desc_of_dev(dev_count).constr       = dev_constr;
    desc_of_dev(dev_count).conv_constr  = dev_conv_constr;
    desc_of_dev(dev_count).params       = dev_params;
    
    pval = [];  % p-axis discretized in the feasible portion
    qmax = [];  % max q values at the discrete (feasible) p values
    qmin = [];  % min q values at the discrete (feasible) p values
    for j = 1:length(dev_constr)
        pval_temp = linspace(dev_constr{j}.prange(1),dev_constr{j}.prange(2),min(max_count,1+floor(diff(dev_constr{j}.prange)/p_step)));
        qmax_temp = double(subs(dev_constr{j}.qrange(2),p,pval_temp));
        qmin_temp = double(subs(dev_constr{j}.qrange(1),p,pval_temp));
        
        pval = [pval pval_temp];
        qmax = [qmax qmax_temp];
        qmin = [qmin qmin_temp];
    end
    
    desc_of_dev(dev_count).pval = pval;
    desc_of_dev(dev_count).qmax = qmax;
    desc_of_dev(dev_count).qmin = qmin;
    
    ac_range = ac_range + [max(pval) min(pval) max(qmax) min(qmin)];
end

aggr_dev(2).params.prated = ac_range(1);
aggr_dev(2).params.powfac = ac_range(3)/ac_range(1);
[aggr_dev(2).constr,~,~] = ac_model(aggr_dev(2).params);

disp('done with ac')
for i = 1:length(pv_pop)
    dev_count = dev_count + 1;
    
    aggr_dev(3).params.pgenmax = aggr_dev(3).params.pgenmax + pv_pop(i).pgenmax;
    aggr_dev(3).params.invcap = aggr_dev(3).params.invcap + pv_pop(i).invcap;
    
    desc_of_dev(dev_count).type = 'photovoltaic';
    [dev_constr,dev_conv_constr,dev_params] = pv_model(pv_pop(i));
    desc_of_dev(dev_count).constr       = dev_constr;
    desc_of_dev(dev_count).conv_constr  = dev_conv_constr;
    desc_of_dev(dev_count).params       = dev_params;
    
    pval = [];  % p-axis discretized in the feasible portion
    qmax = [];  % max q values at the discrete (feasible) p values
    qmin = [];  % min q values at the discrete (feasible) p values
    for j = 1:length(dev_constr)
        pval_temp = linspace(dev_constr{j}.prange(1),dev_constr{j}.prange(2),min(max_count,1+floor(diff(dev_constr{j}.prange)/p_step)));
        qmax_temp = double(subs(dev_constr{j}.qrange(2),p,pval_temp));
        qmin_temp = double(subs(dev_constr{j}.qrange(1),p,pval_temp));
        
        pval = [pval pval_temp];
        qmax = [qmax qmax_temp];
        qmin = [qmin qmin_temp];
    end
    
    desc_of_dev(dev_count).pval = pval;
    desc_of_dev(dev_count).qmax = qmax;
    desc_of_dev(dev_count).qmin = qmin;
    
    pv_range = pv_range + [max(pval) min(pval) max(qmax) min(qmin)];
end

aggr_dev(3).params.pgenmax = -pv_range(2);
aggr_dev(3).params.invcap = pv_range(3);
[aggr_dev(3).constr,~,~] = pv_model(aggr_dev(3).params);

disp('done with pv');
for i = 1:length(bat_pop)
    dev_count = dev_count + 1;
    
    aggr_dev(4).params.prated = aggr_dev(4).params.prated + bat_pop(i).prated;
    aggr_dev(4).params.invcap = aggr_dev(4).params.invcap + bat_pop(i).invcap;
    
    desc_of_dev(dev_count).type = 'battery';
    [dev_constr,dev_conv_constr,dev_params] = bat_model(bat_pop(i));
    desc_of_dev(dev_count).constr       = dev_constr;
    desc_of_dev(dev_count).conv_constr  = dev_conv_constr;
    desc_of_dev(dev_count).params       = dev_params;
    
    pval = [];  % p-axis discretized in the feasible portion
    qmax = [];  % max q values at the discrete (feasible) p values
    qmin = [];  % min q values at the discrete (feasible) p values
    for j = 1:length(dev_constr)
        pval_temp = linspace(dev_constr{j}.prange(1),dev_constr{j}.prange(2),min(max_count,1+floor(diff(dev_constr{j}.prange)/p_step)));
        qmax_temp = double(subs(dev_constr{j}.qrange(2),p,pval_temp));
        qmin_temp = double(subs(dev_constr{j}.qrange(1),p,pval_temp));
        
        pval = [pval pval_temp];
        qmax = [qmax qmax_temp];
        qmin = [qmin qmin_temp];
    end
    
    desc_of_dev(dev_count).pval = pval;
    desc_of_dev(dev_count).qmax = qmax;
    desc_of_dev(dev_count).qmin = qmin;
    
    bat_range = bat_range + [max(pval) min(pval) max(qmax) min(qmin)];
end

aggr_dev(4).params.prated = bat_range(1);
aggr_dev(4).params.invcap = bat_range(3);
[aggr_dev(4).constr,~,~] = bat_model(aggr_dev(4).params);

disp('done with bat')
%===================================
% PROBLEM: Polytope Outer
%===================================

% use a tighest box constraint

all_range = wh_range + ac_range + pv_range + bat_range;
F_adc = [1 0; -1 0; 0 1; 0 -1];
D_adc = [all_range(1) -all_range(2) all_range(3) -all_range(4)]';

end

function [constr, conv_constr, parameters] = wh_model(varargin)

syms p q d
if nargin ==0
    run('params.m')
    
    parameters.prated = prated;
else
    parameters = varargin{1};
    prated = parameters.prated;
end

constr{1}.prange = [0 0];
constr{1}.qrange = [0 0];
constr{1}.dqrange = [0 0];

constr{2}.prange = [prated prated];
constr{2}.qrange = [0 0];
constr{2}.dqrange = [0 0];

conv_constr{1}.prange = [0 prated];
conv_constr{1}.qrange = [0 0];
conv_constr{1}.dqrange = [0 0];

end

function [constr, conv_constr, parameters] = ac_model(varargin)

syms p q d
if nargin == 0
    run('params.m')
    
    parameters.prated = prated;
    parameters.powfac = powfac;
else
    parameters = varargin{1};
    prated = parameters.prated;
    powfac = parameters.powfac;
end

constr{1}.prange = [0 0];
constr{1}.qrange = [0 0];
constr{1}.dqrange = [0 0];

constr{2}.prange = [prated prated];
constr{2}.qrange = [powfac*p powfac*p];
constr{2}.dqrange = [powfac powfac];

conv_constr{1}.prange = [0 prated];
conv_constr{1}.qrange = [powfac*p powfac*p];
conv_constr{1}.dqrange = [powfac powfac];

end

function [constr, conv_constr, parameters] = pv_model(varargin)

syms p q d
if nargin == 0
    run('params.m')
    
    parameters.pgenmax = pgenmax;
    parameters.invcap = invcap;
else
    parameters = varargin{1};
    pgenmax = parameters.pgenmax;
    invcap = parameters.invcap;
end

if pgenmax >= invcap % under-sized inverter
    pgenmax = (1-1e-6)*invcap;
end

constr{1}.prange = [-pgenmax 0];
constr{1}.qrange = [-sqrt(invcap^2-p^2) sqrt(invcap^2-p^2)];
constr{1}.dqrange = [diff(-sqrt(invcap^2-p^2)) diff(sqrt(invcap^2-p^2))];

conv_constr = constr;

end

function [constr, conv_constr, parameters] = bat_model(varargin)

syms p q d
if nargin==0
    run('params.m')
    
    parameters.prated = prated;
    parameters.invcap = invcap;
else
    parameters = varargin{1};
    prated = parameters.prated;
    invcap = parameters.invcap;
end

if prated >= invcap % under-sized inverter
    prated = (1-1e-6)*invcap;
end

constr{1}.prange = [-prated prated];
constr{1}.qrange = [-sqrt(invcap^2-p^2) sqrt(invcap^2-p^2)];
constr{1}.dqrange = [diff(constr{1}.qrange(1)) diff(constr{1}.qrange(2))];

conv_constr = constr;

end
