function [Fout_adc,Dout_adc] = ...
	basic_2_1_vec( ...
	ewh_name,ewh_prated, ...
	ac_name,ac_prated,ac_powfac, ...
	batt_name,batt_prated,batt_invcap, ...
	pv_name,pv_pgenmax,pv_invcap )

	% build struct array ewh_pop
	ewh_pop = struct();
	if length(ewh_name) ~= length(ewh_prated)
		fprintf('WARNING: ewh vectors not same length\n');
	else
		for ii = 1:length(ewh_name)
			ewh_pop.name = ewh_name{ii};
			ewh_pop.prated = ewh_prated{ii};
		end
	end

	% build struct array ac_pop
	ac_pop = struct();
	if length(ac_name) ~= length(ac_prated) || length(ac_name) ~= length(ac_powfac)
		fprintf('WARNING: ac vectors are not the same length\n');
	else
		for ii = 1:length(ac_name)
			ac_pop.name = ac_name{ii};
			ac_pop.prated = ac_prated{ii};
			ac_pop.powfac = ac_powfac{ii};
		end
	end

	% build struct array batt_pop
	batt_pop = struct();
	if length(batt_name) ~= length(batt_prated) || length(batt_name) ~= length(batt_invcap)
		fprintf('WARNING: batt vectors are not the same length\n');
	else
		for ii = 1:length(batt_name)
			batt_pop.name = batt_name{ii};
			batt_pop.prated = batt_prated{ii};
			batt_pop.invcap = batt_invcap{ii};
		end
	end

	% build struct array pv_pop
	pv_pop = struct();
	if length(pv_name) ~= length(pv_pgenmax) || length(pv_name) ~= length(pv_invcap)
		fprintf('WARNING: batt vectors are not the same length\n');
	else
		for ii = 1:length(pv_name)
			pv_pop.name = pv_name{ii};
			pv_pop.pgenmax = pv_pgenmax{ii};
			pv_pop.invcap = pv_invcap{ii};
		end
	end

	% call the function
	[F,D] = basic_2_1(ewh_pop,ac_pop,batt_pop,pv_pop)
	Fout_adc = F
	Dout_adc = D


