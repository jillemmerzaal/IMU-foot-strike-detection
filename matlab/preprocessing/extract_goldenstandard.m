function [HS_r,HS_l] = extract_goldenstandard(output)
%UNTITLED extract "golden standard"
% % The golden standard is a boolian (True False) heel strike and toe-off 
% % indicator determined from pressure insole measurements. 
% % Heel strike: "insoles_RightFoot_is_step" or "insoles_LeftFoot_is_step"
% % Toe off: "insoles_RightFoot_is_lifted" or "insoles_LeftFoot_is_lifted"


col_names_r = ["time", "insoles_RightFoot_is_step", "insoles_RightFoot_is_lifted"];
col_names_l = ["time", "insoles_LeftFoot_is_step", "insoles_LeftFoot_is_lifted"];

y_right = output(:, col_names_r);
y_left = output(:, col_names_l);

HS_r = y_right(y_right.insoles_RightFoot_is_step =="True",1:2);
HS_l = y_left(y_left.insoles_LeftFoot_is_step=="True", 1:2);

if isempty(HS_r.time)
    HS_r = [];
elseif HS_r.time(1) == 0 
    HS_r = table2array(HS_r(2:end, 1)); 
else
    HS_r = table2array(HS_r(:, 1));  
end 

if isempty(HS_l.time)
    HS_l = [];
elseif HS_l.time(1) == 0
    HS_l = table2array(HS_l(2:end, 1));
else
    HS_l = table2array(HS_l(:, 1));  
end


end

