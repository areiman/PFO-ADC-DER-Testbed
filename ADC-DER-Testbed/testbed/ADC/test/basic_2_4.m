function [new_ewh_tank_setpoint,new_ac_heat_set,new_ac_cool_set,...
			batt_p,batt_q,pv_p,pv_q] = ...
		basic_2_4_ac(Popt,Qopt,ewh_state, ...
		ac_temp,ac_heat_set,ac_cool_set,ac_deadband, ...
		ewh_prated,ewh_qrated,ac_prated,ac_qrated, ...
		batt_prated,batt_qrated,pv_prated,pv_qrated)

	% Determine total power and usage ratio
	prated_tot = 0.0;
	batt_prated_tot = 0.0;
	batt_qrated_tot = 0.0;
	pv_prated_tot = 0.0;
	pv_qrated_tot = 0.0;
	for ii = 1:length(ewh_prated)
		prated_tot = prated_tot + ewh_prated{ii};
	end
	for ii = 1:length(ac_prated)
		prated_tot = prated_tot + ac_prated{ii};
	end
	for ii = 1:length(batt_prated)
		prated_tot = prated_tot + batt_prated{ii};
		batt_prated_tot = batt_prated_tot + batt_prated{ii};
		batt_qrated_tot = batt_qrated_tot + batt_qrated{ii};
	end
	for ii = 1:length(pv_prated)
		prated_tot = prated_tot + pv_prated{ii};
		pv_prated_tot = pv_prated_tot + pv_prated{ii};
		pv_qrated_tot = pv_qrated_tot + pv_qrated{ii};
	end
	usage = Popt / prated_tot;

	if usage > 1
		usage = 1;
	end

	if usage < 0
		usage = 0;
	end

	% UPDATE THE EWH STATE VECTOR
	num_ewh = length(ewh_prated);
	target_ewh_on = round( num_ewh * usage );
	% determine which devices are already on
	on_idxs = [];
	off_idxs = [];
	for idx = 1:num_ewh
		if ewh_state{idx}
			on_idxs(end+1) = idx;
		else
			off_idxs(end+1) = idx;
		end
	end
	% turn ewh on or off as necessary
	if target_ewh_on > length(on_idxs)
		% we need to turn devices on
		for ctr = 1:( target_ewh_on - length(on_idxs) )
			% determine which device to turn on
			idx = randi( length(off_idxs) , 1 );
			% turn that device on
			on_idxs(end+1) = off_idxs(idx);
			off_idxs(idx) = [];
		end
	end
	if target_ewh_on < length(on_idxs) % && (length(on_idxs)~=0 )
		% we need to turn devices off
		for ctr = 1:( length(on_idxs) - target_ewh_on )
			% determine which device to turn off
			idx = randi( length(on_idxs) , 1);
			% turn that device off
			off_idxs(end+1) = on_idxs(idx);
			on_idxs(idx) = [];
		end
	end
	% create the new ewh state vector
	new_ewh_tank_setpoint = zeros(length(ewh_state),1);
	new_ewh_tank_setpoint(on_idxs) = 212;	% boiling setpoint for always on
	new_ewh_tank_setpoint(off_idxs) = 32;	% freezing setpoint for always off

		

	% UPDATE THE AC STATE VECTOR
	num_ac = length(ac_prated);
	target_ac_on = round( num_ac * usage );
	on_idxs = [];
	off_idxs = [];
	for idx = 1:num_ac
		if ac_temp{idx} > ac_cool_set{idx}
			on_idxs(end+1) = idx;
		else
			off_idxs(end+1) = idx;
		end
	end
	% turn acs on or off as necessary
	if target_ac_on > length(on_idxs)
		% we need to turn devices on
		for ctr = 1:( target_ac_on - length(on_idxs) )
			% determine which device to turn on
			idx = randi( length(off_idxs) , 1 );
			% turn that device on
			on_idxs(end+1) = off_idxs(idx);
			off_idxs(idx) = [];
		end
	end
	if target_ewh_on < length(on_idxs)
		% we need to turn devices off
		for ctr = 1:( length(on_idxs) - target_ac_on )
			% determine which device to turn off
			idx = randi( length(on_idxs) , 1);
			% turn that device off
			off_idxs(end+1) = on_idxs(idx);
			on_idxs(idx) = [];
		end
	end
	% create the new ac state vector
	new_ac_heat_set = zeros(num_ac,1);
	new_ac_cool_set = zeros(num_ac,1);
	new_ac_heat_set([on_idxs off_idxs]) = 15;	% we aren't using the heater
	new_ac_cool_set(on_idxs) = 32;				% low setpoint for always on
	new_ac_cool_set(off_idxs) = 212;			% high setpoint for always off


	% UPDATE BATTERY P AND Q
	batt_p = zeros(length(batt_prated),1);
	batt_q = zeros(length(batt_prated),1);
	for ii = 1:length(batt_prated)
		batt_p(ii) = usage * batt_prated{ii};
		batt_q(ii) = usage * batt_qrated{ii};
	end

	% UPDATE PV INVERTER P AND Q
	pv_p = zeros(length(pv_prated),1);
	pv_q = zeros(length(pv_prated),1);
	for ii = 1:length(pv_prated)
		pv_prated{ii};
		pv_qrated{ii};
		pv_p(ii) = usage * pv_prated{ii};
		pv_q(ii) = usage * pv_qrated{ii};
	end


