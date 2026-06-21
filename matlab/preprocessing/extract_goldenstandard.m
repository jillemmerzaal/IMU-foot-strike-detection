function [y_HS, y_FO] = extract_goldenstandard(output)
    %EXTRACT_GOLDENSTANDARD extract the "golden standard" for heel strike and
    %toe off
    % % The golden standard is a boolian (True False) heel strike and toe-off 
    % % indicator determined from pressure insole measurements. 
    % % Heel strike: "insoles_RightFoot_is_step" or "insoles_LeftFoot_is_step"
    % % Toe off: "insoles_RightFoot_is_lifted" or "insoles_LeftFoot_is_lifted"
    
    
    col_names_r = ["time", "insoles_RightFoot_is_step", "insoles_RightFoot_is_lifted"];
    col_names_l = ["time", "insoles_LeftFoot_is_step", "insoles_LeftFoot_is_lifted"];
    
    y_right = output(:, col_names_r);
    y_left = output(:, col_names_l);
    
    % Right leg
    ic_r = table2array(y_right(y_right.insoles_RightFoot_is_step =="True",1));
    tc_r = table2array(y_right(y_right.insoles_RightFoot_is_lifted == "True", 1));

    % Left leg
    ic_l = table2array(y_left(y_left.insoles_LeftFoot_is_step=="True", 1));
    tc_l = table2array(y_left(y_left.insoles_LeftFoot_is_lifted=="True", 1));
    
    % Remove heel strikes at time index 0 -> means that the walking has not yet
    % started
    ic_r = remove_t0(ic_r);
    ic_l = remove_t0(ic_l);
    
    % Ensure firt FO comes AFTER first IC per foot
    tc_r = align_fo_to_hs(ic_r, tc_r);
    tc_l = align_fo_to_hs(ic_l, tc_l);

    % Pair each HS with its following FO
    paired_r = pair_events(ic_r,tc_r, 0);
    paired_l = pair_events(ic_l, tc_l, 1);
        
    timings = sortrows([paired_r; paired_l], 'InitialContact');

    y_HS = [timings.InitialContact, timings.LeftStance];
    y_FO = [timings.TerminalContact, timings.LeftStance];
end


% -------------------------------------------------------------------------
% HELPER FUNCTIONS
function ic = remove_t0(ic)
    if ~isempty(ic) && ic(1)==0
        ic = ic(2:end);
    end
end 

function tc = align_fo_to_hs(ic, tc)
    if ~isempty(ic) && ~isempty(tc)
        while ~isempty(tc) && tc(1) < ic(1)
            tc = tc(2:end);
        end
    end
end

function T = pair_events(ic, tc, foot_label)
    
    tc_matched = nan(length(ic), 1);

    for i =1:length(ic)
        % upper bound
        if i < length(ic)
            upper_bound = ic(i+1);
        else
            upper_bound = inf;
        end 

        % Find first TC satisfying ic(i) < TC < ic(i+1)
        idx = find(tc>ic(i) & tc < upper_bound, 1, "first");
        if ~isempty(idx)
            tc_matched(i) = tc(idx);
        end
    end

    valid = ~isnan(tc_matched);
    T = table(ic(valid), tc_matched(valid), repmat(foot_label, sum(valid),1), ...
        'VariableNames', {'InitialContact', 'TerminalContact', 'LeftStance'});
end