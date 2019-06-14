function [new_ewh_tank_setpoint] = Task_2_4_ewh(ewh_state, ewh_prated, Popt_ewh)

	% Determine total power and usage ratio
	ewh_prated_tot = 0.0;
	for ii = 1:length(ewh_prated)
		ewh_prated_tot = ewh_prated_tot + ewh_prated{ii};
    end

	% UPDATE THE EWH STATE VECTOR
	num_ewh = length(ewh_prated);
	target_ewh_on = round(num_ewh * Popt_ewh/ewh_prated_tot);
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
end