function [results] = RunToolbox1(fld)
%RUNTOOLBOX1 Summary of this function goes here
%   Detailed explanation goes here

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
        results.(subj).(parcours).full_course.y = sortrows(y_timings, 1);

        % ----Run the models----
        [results.(subj).(parcours).full_course.y_hat] = toolbox1(data);
    end

end

