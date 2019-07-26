function [wh_dispatch,ac_dispatch,pv_dispatch,bat_dispatch,rem_dispatch] = disaggregation(node_dispatch,wh_range,ac_range,pv_range,bat_range)

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

ac_dispatch     = rel_dispatch.*(ac_range([1 3])-ac_range([2 4]))   + ac_range([2 4]);
ac_dispatch(2) = ac_dispatch(1) * (ac_range(3)-ac_range(4))/(ac_range(1)-ac_range(2));

    node_dispatch_rest = node_dispatch - ac_dispatch;
all_range_rest = all_range - ac_range;
    rel_dispatch = (node_dispatch_rest - all_range_rest([2 4]))./(all_range_rest([1 3])-all_range_rest([2 4]));
rel_dispatch = min(max(rel_dispatch,0),1);

wh_dispatch     = rel_dispatch.*(wh_range([1 3])-wh_range([2 4]))   + wh_range([2 4]);
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
%fid = fopen('temp.txt', 'w');
 %   fprintf(fid, '%f, %f, %f, %f \n %f, %f\n', pv_range(1), pv_range(2), pv_range(3), pv_range(4), pv_dispatch(1), pv_dispatch(2))
%fprintf(fid, '%f, %f, %f, %f \n %f, %f', bat_range(1), bat_range(2), bat_range(3), bat_range(4), bat_dispatch(1), bat_dispatch(2))
 %   fclose(fid)
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

rem_dispatch = node_dispatch-(wh_dispatch+ac_dispatch+pv_dispatch+bat_dispatch);

if max(abs(rem_dispatch))>1e-6
wh_dispatch
ac_dispatch
pv_dispatch
pv_range
bat_dispatch
bat_range
rem_dispatch
node_dispatch
warning on
    warning('Incorrect distribution')
end



end