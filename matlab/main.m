clear; close all; clc

addpath(genpath("./")) % adds all subfolders of the current working direcotry

% read all file names and extract the first one for testing purposes
root = pwd;
fld = root + "/data";
warning('off','all')
%% Toolbox 1: Kiernan et. al
% https://github.com/DovinKiernan/REID_IMU_Running_Event_ID
% read all files 
fl_X = engine(path=fld, subfolder="data_set", extension=".csv", file="xsens");
fl_X = fl_X(~contains(fl_X, "/._")); % Clean up filenames.

for fn = 1:length(fl_X)
    % ----load the data----
    f_X = fl_X{fn};
    
    % get the subject name and walking course
    C = strsplit(f_X,"/");
    n = length(C);
    
    fprintf('processing walking: %s for subj: %s.\n', C{n-2}, C{n-1})
    subj = string(C{n-1});
    parcours = string(C{n-2});
    
    fname = subj + "_" + parcours;
    % Match outcome file with xsens file
    f_y = fullfile(C{1:n-1}, "labels.csv");
    
    raw_df = readtable(f_X);
    raw_output = readtable(f_y);

    %% Toolbox 1
    % all the available methods in the code published by Kiernan et. al., (2023).
    % ----Preprocessing---- 
    data = preprocessing_t1(raw_df);

    % extract "golden standard"
    [HS_r,HS_l] = extract_goldenstandard(raw_output);

    y_timings_r = [HS_r, zeros(length(HS_r), 1)];
    y_timings_l = [HS_l, ones(length(HS_l), 1)];

    y_timings = [y_timings_r; y_timings_l];
    results.y = sortrows(y_timings, 1);

    % ----Run the models----
    shank_methods = {'Mizrahi', 'Mercer','Purcell', 'AminianODonovan', ...
        'GreeneMcGrath', 'Sinclair', 'Norris', 'Fadillioglu', ...
        'Bach', 'Bach_modified', 'Whelan'};
    
    for a = 1:length(shank_methods)
        algorithm = shank_methods{a};
        results.y_hat = step_detection(data, algorithm, "shank");
        save_fld = fullfile(fld, "toolbox1", algorithm);
        
        if ~exist(save_fld, 'dir')
            mkdir(save_fld)
        end
        fl = fullfile(save_fld, fname);
        save(fl,"results")
        
    end
        
    lb_methods ={'Auvinet', 'Lee', 'Wixted', 'Benson', 'Reenalda'};
    
    for a = 1:length(lb_methods) 
        algorithm = lb_methods{a};
        results.y_hat = step_detection(data, algorithm, "lower_back");
        save_fld = fullfile(fld, "toolbox1", algorithm);
        
        if ~exist(save_fld, 'dir')
            mkdir(save_fld)
        end
        fl = fullfile(save_fld, fname);
        save(fl,"results")
    end
end