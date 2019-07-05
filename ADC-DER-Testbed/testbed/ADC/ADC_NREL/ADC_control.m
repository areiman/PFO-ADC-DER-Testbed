% This code serves as a framework to optimize regional welfare among
% aggregated customers while tracking the reference point of p* and q*.

function [p_pv, q_pv, p_ba, q_ba] = ADC_control(deltat, n_pv, n_ba, cap_pv, p_av, ...
    cap_ba, cap_ba_inverter, p_ba_cha_max, p_ba_dis_max, eff_ba, ...
    SOC_set, SOC_now, p_opt, q_opt)

p_ba_cha_max = - p_ba_cha_max;

SOC_set;
SOC_now;
%fprintf('hi\n');
%class(deltat)
%deltat
%class(cap_ba)
%cap_ba

max_iter=50000;

% inverter output initialization
p_pv = p_av;
% q_pv= zeros(n_pv,1);
q_pv= zeros(1,n_pv);

% battery initialization
soc=SOC_now;
% p_ba=zeros(n_ba,1);
p_ba=zeros(1,n_ba);
q_ba=zeros(1,n_ba);

% dual variable associated with tracking discrepancy
mup=0;
muq=0;

% constant stepsize for primal and dual; tuned
epsilonP=0.005;
epsilonD=0.005;

%% Cost function parameters for PV inverters
% C_i^pv(p_i,q_i)=cost_p (p_i^av-p_i)^2+cost_q q_i^2; parameters can be altered for heterogeneous
% inverters
cost_p = 2 * ones(n_pv,1);
cost_q = 1 * ones(n_pv,1);

%% cost function parameters for batteries

% power-soc convert rate = time/60/battery_capacity
power_SOC_rate = deltat/60./cap_ba;
% C_i^b=cost_bat*(SoC-0.5)^2
cost_bat = deltat*1./power_SOC_rate;
cost_bat_q = 1;


for k=1:max_iter
    % primal update
    for i=1:n_pv
%        p_pv(i,k+1) = p_pv(i,k) - epsilonP * (2 * cost_p(i) * (-p_av(i) + p_pv(i,k)) + mup(k));
%        q_pv(i,k+1) = q_pv(i,k) - epsilonP * (2 * cost_q(i) * q_pv(i,k) + muq(k));
%        [p_pv(i,k+1), q_pv(i,k+1)] = Proj_inverter( p_pv(i,k+1), q_pv(i,k+1), p_av(i), cap_pv(i));
        p_pv(i) = p_pv(i) - epsilonP * (2 * cost_p(i) * (-p_av(i) + p_pv(i)) + mup);
        q_pv(i) = q_pv(i) - epsilonP * (2 * cost_q(i) * q_pv(i) + muq);
        [p_pv(i), q_pv(i)] = Proj_inverter( p_pv(i), q_pv(i), p_av(i), cap_pv(i));
    end
    for i=1:n_ba
%         p_ba(i,k+1) = p_ba(i,k) -  epsilonP * ( - 2 * eff_ba(i) * power_SOC_rate(i)...
%             * cost_bat(i) * (soc(i) - SOC_set(i) + power_SOC_rate(i)*eff_ba(i)*p_ba(i,k)) + mup(k));
        gradient_ba = - 2 * eff_ba(i) * power_SOC_rate(i) ...
            * cost_bat(i) * (soc(i) - SOC_set(i) + power_SOC_rate(i)*eff_ba(i));
        p_ba(i) = p_ba(i) -  epsilonP * ( gradient_ba * p_ba(i) + mup);
        q_ba(i) = q_ba(i) - epsilonP * ( cost_bat_q * q_ba(i) + muq);

%         % Battery rates projection
%         if p_ba(i,k+1) > p_ba_dis_max(i)
%             p_ba(i,k+1) = p_ba_dis_max(i);
%         elseif p_ba(i,k+1) < p_ba_cha_max(i)
%             p_ba(i,k+1) = p_ba_cha_max(i);
%         end
        % Battery rates projection

        [p_ba(i), q_ba(i)] = Proj_ba_inverter( p_ba(i), q_ba(i), p_ba_dis_max(i), p_ba_cha_max(i), cap_ba_inverter(i));


%         if p_ba(i) > p_ba_dis_max(i)
%             p_ba(i) = p_ba_dis_max(i);
%         elseif p_ba(i) < p_ba_cha_max(i)
%             p_ba(i) = p_ba_cha_max(i);
%         end
    end

    % dual update
%     mup(k+1) = mup(k) + epsilonD * (sum(p_pv(:,k)) + sum(p_ba(:,k)) - p_opt);
%     muq(k+1) = muq(k) + epsilonD * (sum(q_pv(:,k)) - q_opt);
    mup = mup + epsilonD * (sum(p_pv) + sum(p_ba) - p_opt);
    muq = muq + epsilonD * (sum(q_pv) + sum(q_ba) - q_opt);

end

% mup = mup
% muq = muq
% plot(mup);hold on; plot(muq);% plot dual variable
% figure;
% plot(p_ba(5,:));
end
