function [F_adc,D_adc,wh_range,ac_range,pv_range,bat_range] = dom_approx_box(varargin)

tic;

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
sum_Qmax = varargin{5};
sum_Qmin = varargin{6};
scale_factor = sqrt(varargin{7});

if nargin>7
    addpath(genpath(varargin{8}))
end

%==========================================================
% Create a random population of devices
% Enter the type: battery, ewh, hvac, photovoltaic, wind
%==========================================================
wh_range = zeros(1,4);
ac_range = zeros(1,4);
pv_range = zeros(1,4);
bat_range = zeros(1,4);

dev_count = 0;

for i = 1:length(wh_pop)
    dev_count = dev_count + 1;    
    dev_constr = wh_model(wh_pop(i));    
    wh_range = wh_range + [dev_constr.prange(2) dev_constr.prange(1) dev_constr.qrange(2) dev_constr.qrange(1)];
end
wh_range_old = wh_range;
    wh_range(1) = (wh_range_old(1)+wh_range_old(2))/2 + scale_factor*(wh_range_old(1)-wh_range_old(2))/2;
    wh_range(2) = (wh_range_old(1)+wh_range_old(2))/2 - scale_factor*(wh_range_old(1)-wh_range_old(2))/2;
    wh_range(3) = (wh_range_old(3)+wh_range_old(4))/2 + scale_factor*(wh_range_old(3)-wh_range_old(4))/2;
    wh_range(4) = (wh_range_old(3)+wh_range_old(4))/2 - scale_factor*(wh_range_old(3)-wh_range_old(4))/2;
disp('    done with wh')

for i = 1:length(ac_pop)
    dev_count = dev_count + 1;    
    dev_constr = ac_model(ac_pop(i));    
    ac_range = ac_range + [dev_constr.prange(2) dev_constr.prange(1) dev_constr.qrange(2) dev_constr.qrange(1)];
end
pf_ratio =  ac_range(3)/ac_range(1);
ac_range(1) = min(ac_range(1), sum_Qmax);
ac_range(2) = max(ac_range(2), sum_Qmin);
ac_range(3) = ac_range(1)*pf_ratio;
ac_range(4) = ac_range(2)*pf_ratio;
ac_range_old = ac_range;
    ac_range(1) = (ac_range_old(1)+ac_range_old(2))/2 + scale_factor*(ac_range_old(1)-ac_range_old(2))/2;
    ac_range(2) = (ac_range_old(1)+ac_range_old(2))/2 - scale_factor*(ac_range_old(1)-ac_range_old(2))/2;
    ac_range(3) = (ac_range_old(3)+ac_range_old(4))/2 + scale_factor*(ac_range_old(3)-ac_range_old(4))/2;
    ac_range(4) = (ac_range_old(3)+ac_range_old(4))/2 - scale_factor*(ac_range_old(3)-ac_range_old(4))/2;
disp('    done with ac')

for i = 1:length(pv_pop)
    dev_count = dev_count + 1;    
    dev_constr = pv_model(pv_pop(i));
    pv_range = pv_range + [dev_constr.prange(2) dev_constr.prange(1) dev_constr.qrange(2) dev_constr.qrange(1)];
end
pv_range_old = pv_range;
    pv_range(1) = (pv_range_old(1)+pv_range_old(2))/2 + scale_factor*(pv_range_old(1)-pv_range_old(2))/2;
    pv_range(2) = (pv_range_old(1)+pv_range_old(2))/2 - scale_factor*(pv_range_old(1)-pv_range_old(2))/2;
    pv_range(3) = (pv_range_old(3)+pv_range_old(4))/2 + scale_factor*(pv_range_old(3)-pv_range_old(4))/2;
    pv_range(4) = (pv_range_old(3)+pv_range_old(4))/2 - scale_factor*(pv_range_old(3)-pv_range_old(4))/2;
disp('    done with pv');

for i = 1:length(bat_pop)
    dev_count = dev_count + 1;    
    dev_constr = bat_model(bat_pop(i));
    bat_range = bat_range + [dev_constr.prange(2) dev_constr.prange(1) dev_constr.qrange(2) dev_constr.qrange(1)];;
end
bat_range_old = bat_range;
    bat_range(1) = (bat_range_old(1)+bat_range_old(2))/2 + scale_factor*(bat_range_old(1)-bat_range_old(2))/2;
    bat_range(2) = (bat_range_old(1)+bat_range_old(2))/2 - scale_factor*(bat_range_old(1)-bat_range_old(2))/2;
    bat_range(3) = (bat_range_old(3)+bat_range_old(4))/2 + scale_factor*(bat_range_old(3)-bat_range_old(4))/2;
    bat_range(4) = (bat_range_old(3)+bat_range_old(4))/2 - scale_factor*(bat_range_old(3)-bat_range_old(4))/2;
disp('    done with bat')
%===================================
% PROBLEM: Polytope Outer
%===================================

% use a tighest box constraint

all_range = wh_range + ac_range + pv_range + bat_range;
F_adc = [1 0; -1 0; 0 1; 0 -1];
D_adc = [all_range(1) -all_range(2) all_range(3) -all_range(4)]';

toc


end

function constr = wh_model(varargin)

parameters = varargin{1};
prated = parameters.prated;

constr.prange = [0 prated];
constr.qrange = [0 0];

end

function constr = ac_model(varargin)

parameters = varargin{1};
prated = parameters.prated;
powfac = parameters.powfac;

constr.prange = [0 prated];
constr.qrange = [0 powfac*prated];

end

function constr = pv_model(varargin)

parameters = varargin{1};
pgenmax = parameters.pgenmax;
invcap = parameters.invcap;

if pgenmax >= invcap % under-sized inverter
    pgenmax = (1-1e-6)*invcap;
end

constr.prange = [-pgenmax 0];
constr.qrange = [-invcap invcap];

end

function constr = bat_model(varargin)

parameters = varargin{1};
prated = parameters.prated;
invcap = parameters.invcap;

if prated >= invcap % under-sized inverter
    prated = (1-1e-6)*invcap;
end

constr.prange = [-prated prated];
constr.qrange = [-invcap invcap];

end