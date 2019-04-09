function [wh_dispatch,ac_dispatch,pv_dispatch,bat_dispatch] = disaggregation(node_dispatch,wh_range,ac_range,pv_range,bat_range)

%% INPUT 
% node_dispatch     : 1x2 array with the ADC P and Q dispatch values
% wh_range          : 1x4 array of pmax,pmin,qmax,qmin of EWHs
% ac_range          : 1x4 array of pmax,pmin,qmax,qmin of ACs
% pv_range          : 1x4 array of pmax,pmin,qmax,qmin of PVs
% bat_range         : 1x4 array of pmax,pmin,qmax,qmin of batteries

% wh_dispatch       : 1x2 array with the WH P and Q values
% ac_dispatch       : 1x2 array with the AC P and Q values
% pv_dispatch       : 1x2 array with the PV P and Q values
% bat_dispatch      : 1x2 array with the Bat P and Q values
%%

all_range = wh_range + ac_range + pv_range + bat_range;
rel_dispatch = (node_dispatch - all_range([2 4]))./(all_range([1 3])-all_range([2 4]));


wh_dispatch     = rel_dispatch.*(wh_range([1 3])-wh_range([2 4]))   + wh_range([2 4]);
ac_dispatch     = rel_dispatch.*(ac_range([1 3])-ac_range([2 4]))   + ac_range([2 4]);
pv_dispatch     = rel_dispatch.*(pv_range([1 3])-pv_range([2 4]))   + pv_range([2 4]);
bat_dispatch    = rel_dispatch.*(bat_range([1 3])-bat_range([2 4])) + bat_range([2 4]);


% sanity checks
if max(prod(wh_dispatch(1)-wh_range([1 2])),prod(wh_dispatch(2)-wh_range([3 4])))>=1e-9
    wh_range
    wh_dispatch
    error('Incorrect WH assignment')
end
if max(prod(ac_dispatch(1)-ac_range([1 2])),prod(ac_dispatch(2)-ac_range([3 4])))>=1e-9
    ac_range
    ac_dispatch
    error('Incorrect AC assignment')
end
if max(prod(pv_dispatch(1)-pv_range([1 2])),prod(pv_dispatch(2)-pv_range([3 4])))>=1e-9
    pv_range
    pv_dispatch
    error('Incorrect PV assignment')
end
if max(prod(bat_dispatch(1)-bat_range([1 2])),prod(bat_dispatch(2)-bat_range([3 4])))>=1e-9
    bat_range
    bat_dispatch
    error('Incorrect BAT assignment')
end
if max(abs(wh_dispatch+ac_dispatch+pv_dispatch+bat_dispatch-node_dispatch))>1e-6
    error('Incorrect distribution')
end

end