function results = RunSegmentedToolbox1(fld)

% read all files 
fl_y = engine(path=fld, subfolder="data_set", extension=".csv", file="labels");
fl_X = engine(path=fld, subfolder="data_set", extension=".csv", file="xsens");

for fn = 1:length(fl_X)

    % load the data
    f_y = fl_y{fn};
    f_X = fl_X{fn};
    
    % get the subject name and walking course
    C = strsplit(f_X,"/");
    fprintf('processing walking: %s subj: %s.\n', C{10}, C{11})
    subj = string(C{11});
    parcours = string(C{10});
    
    % read the raw data to tables
    raw_output = readtable(f_y);
    raw_df = readtable(f_X);
    
    % Preprocessing 
    % i.e. Extrect relevant columns, rotate from local to global, and match the
    % local coordinate system of toolbox 1
    data_t1 = preprocessing_t1(raw_df);

    %% From here it is different
    % Detect the change points of the walk mode
    walk_modes = raw_output.walk_mode;
    changePoints = find(~strcmp(walk_modes(1:end-1), walk_modes(2:end)));
    changePoints = [0; changePoints];
    
    % Seperate the walk modes
    counter = 0;
    for c = 1:length(changePoints)-1
        counter = counter + 1; 
        start_mode = changePoints(c) + 1;
        end_mode = changePoints(c+1);
        fprintf('   analysing: section_%s.\n',  + num2str(counter))
        %% segmented data frames
        % Xsens data
        fields = fieldnames(data_t1);
        for f = 1:length(fields)
            field = fields{f};
            segmented_data.(field) = data_t1.(field)(start_mode:end_mode, :);
            
            if field == "X_pelvis" || field == "X_Rshank" || field == "X_Lshank"
                initial_time = segmented_data.(field)(1,1);
                segmented_data.(field)(:,1) = segmented_data.(field)(:,1) - initial_time;
            end
        end
    
        % label data
        segmented_output = raw_output(start_mode:end_mode, :);
        % reset time. 
        % initial_time = segmented_output.time(1,1);
        segmented_output.time = segmented_output.time - initial_time;
        results.(subj).(parcours).("section_" + num2str(counter)).get_walk_mode = segmented_output.walk_mode(1);
    
        % extract "golden standard"
        [HS_r,HS_l] = extract_goldenstandard(segmented_output);
        
        y_timings_r = [HS_r, zeros(length(HS_r), 1)];
        y_timings_l = [HS_l, ones(length(HS_l), 1)];
        
        y_timings = [y_timings_r; y_timings_l];
        results.(subj).(parcours).("section_" + num2str(counter)).y = sortrows(y_timings, 1);
    
    
        % Run the models
        [results.(subj).(parcours).("section_" + num2str(counter)).y_hat] = toolbox1(segmented_data);
        
        clear segmented_data segmented_output
    end % end inner loop surface changes 

end % outer loop, all files

end% end function

