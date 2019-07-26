function [Fout_adc,Dout_adc,ewh_range,ac_range,pv_range,batt_range] = ...
	basic_2_1_vec( ...
	ewh_name,ewh_prated, ...
	ac_name,ac_prated,ac_powfac, ...
	batt_name,batt_prated,batt_invcap, ...
	pv_name,pv_pgenmax,pv_invcap, sum_Qmax, sum_Qmin, scale_factor)

	addpath('../ADC/ADC_flex/functions/')

	% build struct array ewh_pop
	ewh_pop = struct('name',{});
	if length(ewh_name) ~= length(ewh_prated)
		fprintf('WARNING: ewh vectors not same length\n');
	else
		for ii = 1:length(ewh_name)
			ewh_pop(ii).name = ewh_name{ii};
			ewh_pop(ii).prated = ewh_prated{ii};
		end
	end

	% build struct array ac_pop
	ac_pop = struct('name',{});
	if length(ac_name) ~= length(ac_prated) || length(ac_name) ~= length(ac_powfac)
		fprintf('WARNING: ac vectors are not the same length\n');
	else
		for ii = 1:length(ac_name)
			ac_pop(ii).name = ac_name{ii};
			ac_pop(ii).prated = ac_prated{ii};
			ac_pop(ii).powfac = ac_powfac{ii};
		end
	end

	% build struct array batt_pop
	batt_pop = struct('name',{});
	if length(batt_name) ~= length(batt_prated) || length(batt_name) ~= length(batt_invcap)
		fprintf('WARNING: batt vectors are not the same length\n');
	else
		for ii = 1:length(batt_name)
			batt_pop(ii).name = batt_name{ii};
			batt_pop(ii).prated = batt_prated{ii};
			batt_pop(ii).invcap = batt_invcap{ii};
		end
	end

	% build struct array pv_pop
	pv_pop = struct('name',{});
	if length(pv_name) ~= length(pv_pgenmax) || length(pv_name) ~= length(pv_invcap)
		fprintf('WARNING: pv vectors are not the same length\n');
	else
		for ii = 1:length(pv_name)
			pv_pop(ii).name = pv_name{ii};
			pv_pop(ii).pgenmax = pv_pgenmax{ii};
			pv_pop(ii).invcap = pv_invcap{ii};
		end
	end

	% call the function
	[Fout_adc,Dout_adc,ewh_range,ac_range,pv_range,batt_range] = ...
		dom_approx_box(ewh_pop,ac_pop,pv_pop,batt_pop, sum_Qmax, sum_Qmin, scale_factor);

