function [P,Q] = Proj_inverter(xt, yt, Ux, Sx);

theta = atan(sqrt(Sx^2 - Ux^2)/Ux);
theta_t = atan(yt/xt);


if xt^2 + yt^2 <= Sx^2 && xt <= Ux
     x2 = xt;
     y2 = yt;
else
    if  abs(theta_t) > theta        
        xx = [xt yt].'*Sx/sqrt((xt^2 + yt^2));
        x2 = xx(1);
        y2 = xx(2); 
    end 
    if  abs(theta_t) <= theta  
        if abs(yt) > sqrt(Sx^2 - Ux^2)
            x2 = Ux;
            y2 = sqrt(Sx^2 - Ux^2);
        else
            x2 = Ux;
            y2 = yt;
        end
    end

end
    
P = x2;
Q = y2;
