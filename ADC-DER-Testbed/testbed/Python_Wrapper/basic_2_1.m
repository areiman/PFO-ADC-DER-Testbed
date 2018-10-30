function [Fout_adc,Dout_adc] = ...
    basic_2_1(ewh_pop, hvac_pop, battery_pop, photovoltaic_pop)

	Pmax = 0;
	Qmax = 0;

    for ewh = ewh_pop
		ewh
        fprintf('%s\n',ewh.name);
        fprintf('\tprated: %f\n',ewh.prated);
		Pmax = Pmax + ewh.prated;
    end
    
    for hvac = hvac_pop
		hvac
        fprintf('%s\n',hvac.name);
        fprintf('\tprated: %f\n',hvac.prated);
        fprintf('\tpowfac: %f\n',hvac.powfac);
		Pmax = Pmax + hvac.prated;
		Qmax = Qmax + hvac.prated * hvac.powfac;
		fprintf('\tQ_calc: %f\n',hvac.prated*hvac.powfac);
    end
    
    for batt = battery_pop
		batt
        fprintf('%s\n',batt.name);
        fprintf('\tprated: %f\n',batt.prated);
        fprintf('\tinvcap: %f\n',batt.invcap);
		Pmax = Pmax + batt.prated;
		Qmax = Qmax + batt.prated;
    end
    
    for pv = photovoltaic_pop
		pv
        fprintf('%s\n',pv.name);
        fprintf('\tpgenmax: %f\n',pv.pgenmax);
        fprintf('\tinvcap: %f\n',pv.invcap);
		Pmax = Pmax + pv.pgenmax;
		Qmax = Qmax + pv.invcap;
    end

	% draw a box from (0,0) to (Pmax,Qmax) -> m = 4
	% output to PFO
	% Fout_adc * [x;y] <= Dout_adc
    Fout_adc = ones(4,2);	% matrix m x 2 | m is number of sides of polygon
    Dout_adc = zeros(4,1);	% matrix m x 1
	% -1*x + 0*y <= 0
	Fout_adc(1,:) = [-1,0];
	Dout_adc(1) = 0;
	% 0*x + -1*y <= 0
	Fout_adc(2,:) = [0,-1];
	Dout_adc(2) = 0;
	% 1*x + 0*y <= Pmax
	Fout_adc(3,:) = [1,0];
	Dout_adc(3) = Pmax;
    % 0*x + 1*y <= Qmax
	Fout_adc(4,:) = [0,1];
	Dout_adc(4) = Qmax;

end
