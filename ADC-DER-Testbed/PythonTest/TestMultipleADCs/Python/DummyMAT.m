function [ keys , KeyVal ] = DummyMAT( SubKeys )% , SubKyesVal )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

%SubKeys = Test(SubKeys);
%fid_sub_Source  = fopen('Matlab.txt', 'w' );
%for i = 1: length(SubKeys)
%	fprintf(fid_sub_Source, '%s\r\n', SubKeys{i} );
%end
%fclose(fid_sub_Source) 

%     Directory = 'C:\Users\bhat538\Desktop\ControlTheory\ConfigFilesBishnu\PythonScripts\';
     FileName = 'GLD_Sub_Kyes';
%     fid_sub_Source  = fopen(strcat( Directory, strcat( FileName, '.cfg') ), 'r');
    
    fid_sub_Source  = fopen(strcat( FileName, '.cfg'), 'r' );
    
    %% Searching load information from the feeders
    tline1 = fgetl( fid_sub_Source );
    Counter = 1;
    while ischar(tline1)
        Keys{Counter} = tline1 ;
        tline1 = fgetl( fid_sub_Source  );
        Counter = Counter + 1 ;
    end
    
    keys = Keys;
    Len = length (keys);
    for i = 1 : Len
        if contains (keys{i}, 'heating_setpoint')
            KeyVal(i) = 70 * (1 + randi(5, 1)/100 );
        elseif contains (keys{i}, 'cooling_setpoint')
            KeyVal(i) = 75 * (1 + randi(5, 1)/100 );
        elseif contains (keys{i}, 'tank_setpoint')
            KeyVal(i) = 130 * (1 + randi(5, 1)/100 );
        elseif contains (keys{i}, 'P_Out')
            KeyVal(i) = 0 * (1 + randi(5, 1)/100 );
        elseif contains (keys{i}, 'Q_Out')
            KeyVal(i) = 0 * (1 + randi(5, 1)/100 );
        end     
    end
    
end

