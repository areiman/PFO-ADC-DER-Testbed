function [P,Q] = Proj_ba_inverter(xt, yt, Ux, Lx, Sx)

% theta = atan(sqrt(Sx^2 - Ux^2)/Ux);
%theta_t = atan(yt/xt);

%% Within range, do nothing
if xt^2 + yt^2 <= Sx^2 && xt <= Ux && xt >=Lx
     x2 = xt;
     y2 = yt;
%% Out of range, do the following
else
    % If p is positive
    if xt > 0
        theta = atan(sqrt(Sx^2 - Ux^2)/Ux);
        theta_t = atan(yt/xt);
        if  abs(theta_t) > theta
            xx = [xt yt].'*Sx/sqrt((xt^2 + yt^2));
            x2 = xx(1);
            y2 = xx(2);
        else  %if  abs(theta_t) <= theta
            if abs(yt) > sqrt(Sx^2 - Ux^2)
                x2 = Ux;
                y2 = sqrt(Sx^2 - Ux^2);
            else
                x2 = Ux;
                y2 = yt;
            end
        end
    % if p is zero, atan does not exist
    elseif xt ==0
        x2 = 0;
        if yt > Sx
            y2 = Sx;
        elseif yt < -Sx
            y2 = -Sx;
        else
            y2 = yt;
        end
    % If p is negative, switch the sign of p and do the same as in p > 0
    else % if xt < 0
        xt = -xt;
        Ux = -Lx;
        theta = atan(sqrt(Sx^2 - Ux^2)/Ux);
        theta_t = atan(yt/xt);
        if  abs(theta_t) > theta
            xx = [xt yt].'*Sx/sqrt((xt^2 + yt^2));
            x2 = xx(1);
            y2 = xx(2);
        else   %if  abs(theta_t) <= theta
            if abs(yt) > sqrt(Sx^2 - Ux^2)
                x2 = Ux;
                y2 = sqrt(Sx^2 - Ux^2);
            else
                x2 = Ux;
                y2 = yt;
            end
        end
        x2 = -x2;
    end
end

P = x2;
Q = y2;
