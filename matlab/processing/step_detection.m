function [y_hat] = step_detection(data, algorithm, location)
%STEP_DETECTION Code to perform step detection using "Toolbox 1" 
%   Detailed explanation goes here

    X_Lshank = data.X_Lshank;
    X_Rshank = data.X_Rshank;
    X_pelvis = data.X_pelvis;
   
    switch location
        case "shank"
            [timings_l, ~, ~] = REID_IMU_Running_Event_ID(X_Lshank, algorithm, 'Left shank');
            [timings_r, ~, ~] = REID_IMU_Running_Event_ID(X_Rshank, algorithm, 'Right shank');

            if timings_r.initial_contact(1) == 0 || timings_r.initial_contact(1) == -1
                timings_r.initial_contact(1) = 1;
            end

            if timings_l.initial_contact(1) == 0 || timings_l.initial_contact(1) == -1
                timings_l.initial_contact(1) = 1;
            end

            if isnan(timings_r.initial_contact)
                timings_r = array2table(zeros(0,3));
                timings_r.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
            end
                
            if isnan(timings_l.initial_contact)
                timings_l = array2table(zeros(0,3));
                timings_l.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
            end
            
            % create heel strike and toe off tabels of the method
            HS_r_hat = [X_Rshank(timings_r.initial_contact, 1), timings_r.left_stance];
            HS_l_hat = [X_Lshank(timings_l.initial_contact, 1), timings_l.left_stance]; 
    
            y_hat_timings = [HS_r_hat;HS_l_hat];
            y_hat = sortrows(y_hat_timings);

        case "lower_back"
            try 
                [timings, ~, ~] = REID_IMU_Running_Event_ID(X_pelvis, algorithm);
            catch
                timings = array2table(zeros(0,3));
                timings.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
            end
    
    
            try 
                y_hat = [X_pelvis(timings.initial_contact, 1), timings.left_stance];
            catch ME
                switch ME.identifier
                    case 'MATLAB:badsubscript'
                        timings = array2table(zeros(0,3));
                        timings.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
                        y_hat = [X_pelvis(timings.initial_contact, 1), timings.left_stance];
                end
            end
    end
end
%     if m <= shank_methods % ----These are the shank methods----
%         sensor{m, 1} = 'shank';
%         method{m, 1} = all_methods{m};
%         % try % if the method produces an error, than code will break and no results will be written  
%             [timings_l, ~, ~] = REID_IMU_Running_Event_ID(X_Lshank, ...
%                 all_methods{m}, 'Left shank');
%             [timings_r, ~, ~] = REID_IMU_Running_Event_ID(X_Rshank, ...
%                 all_methods{m}, 'Right shank');
% 
%             if timings_r.initial_contact(1) == 0 || timings_r.initial_contact(1) == -1
%                 timings_r.initial_contact(1) = 1;
%             end
% 
%             if timings_l.initial_contact(1) == 0 || timings_l.initial_contact(1) == -1
%                 timings_l.initial_contact(1) = 1;
%             end
% 
%         % catch
%         %     timings_l = array2table(zeros(0,3));
%         %     timings_r = array2table(zeros(0,3));
%         %     timings_l.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%         %     timings_r.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%         % end
% 
%         if isnan(timings_r.initial_contact)
%             timings_r = array2table(zeros(0,3));
%             timings_r.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%         end
% 
%         if isnan(timings_l.initial_contact)
%             timings_l = array2table(zeros(0,3));
%             timings_l.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%         end
% 
%         % create heel strike and toe off tabels of the method
%         HS_r_hat = [X_Rshank(timings_r.initial_contact, 1), timings_r.left_stance];
%         HS_l_hat = [X_Lshank(timings_l.initial_contact, 1), timings_l.left_stance]; 
% 
%         y_hat_timings = [HS_r_hat;HS_l_hat];
%         y_hat.(all_methods{m}) = sortrows(y_hat_timings);
% 
%         clear timings_l timings_r
% 
%     else % ----These are the sacrum/lower back----
%         sensor{m, 1} = 'lower back';
%         method{m, 1} = all_methods{m};
% 
%         try 
%             [timings, ~, ~] = REID_IMU_Running_Event_ID(X_pelvis, all_methods{m});
%         catch
%             timings = array2table(zeros(0,3));
%             timings.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%         end
% 
% 
%         %###### TODO: Test if this also works for the full course data.
%         % This was created for the segmented data. 
%         try 
%             y_hat.(all_methods{m}) = [X_pelvis(timings.initial_contact, 1), timings.left_stance];
%         catch ME
%             switch ME.identifier
%                 case 'MATLAB:badsubscript'
%                     timings = array2table(zeros(0,3));
%                     timings.Properties.VariableNames = {'initial_contact', 'terminal_contact', 'left_stance'};
%                     y_hat.(all_methods{m}) = [X_pelvis(timings.initial_contact, 1), timings.left_stance];
%             end
%         end
% 
%     end % sensor position 
% 
% 
%     % results = table(sensor, method, accuracy_ic, mae_ic);
% end

