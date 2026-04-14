function [data] = preprocessing_t1(df)
%PREPROCESSING_T1 Processes the data so it is suitable for "Toolbox 1" 
%   Detailed explanation goes here

    data.raw_pelvis_acc = table2array(df(:, ["acceleration_Pelvis_x", ...
        "acceleration_Pelvis_y",...
        "acceleration_Pelvis_z"]));
    
    data.raw_pelvis_gyro =table2array(df(:, ["angularVelocity_Pelvis_x", ...
        "angularVelocity_Pelvis_y", ...
        "angularVelocity_Pelvis_z"]));
    
    data.raw_Rshank_acc = table2array(df(:, ["acceleration_RightLowerLeg_x",...
        "acceleration_RightLowerLeg_y",...
        "acceleration_RightLowerLeg_z"]));
        
    data.raw_Rshank_gyro = table2array(df(:, ["angularVelocity_RightLowerLeg_x", ...
        "angularVelocity_RightLowerLeg_y",...
        "angularVelocity_RightLowerLeg_z"]));
    
    data.raw_Lshank_acc = table2array(df(:, ["acceleration_LeftLowerLeg_x", ...
        "acceleration_LeftLowerLeg_y",...
        "acceleration_LeftLowerLeg_z"]));
    
    data.raw_Lshank_gyro = table2array(df(:, ["angularVelocity_LeftLowerLeg_x", ...
        "angularVelocity_LeftLowerLeg_y", ... 
        "angularVelocity_LeftLowerLeg_z"]));
    
    data.quat_pelvis = table2array(df(:, ["orientation_Pelvis_q1", "orientation_Pelvis_qi",...
        "orientation_Pelvis_qj", "orientation_Pelvis_qk"]));
    
    data.quat_Rshank = table2array(df(:, ["orientation_RightLowerLeg_q1", "orientation_RightLowerLeg_qi",...
        "orientation_RightLowerLeg_qj", "orientation_RightLowerLeg_qk"]));
    
    data.quat_Lshank = table2array(df(:, ["orientation_LeftLowerLeg_q1", "orientation_LeftLowerLeg_qi",...
        "orientation_LeftLowerLeg_qj", "orientation_LeftLowerLeg_qk"]));
    
    
    %% Rotate global to local
    % This step is needed because the Xsens link system exports the segment
    % acceleration and segment angular velocity in the global reference frame.
    [data.gyro_local_pelvis, data.acc_local_pelvis] = global2local(data.raw_pelvis_gyro, data.raw_pelvis_acc, data.quat_pelvis);
    [data.gyro_local_Rshank, data.acc_local_Rshank] = global2local(data.raw_Rshank_gyro, data.raw_Rshank_acc, data.quat_Rshank);
    [data.gyro_local_Lshank, data.acc_local_Lshank] = global2local(data.raw_Lshank_gyro, data.raw_Lshank_acc, data.quat_Lshank);
    
    %% Rotate the coordinate system from Xsens needed for Kiernan et al (2023) 
    % following ISB convention. 
    % Meaning x is anterior, y = proximal, and z = right.
    % The xsens segment coordinate system used in the dataset paper (Losing & 
    % Hassenjäger) is as follows: x = forward, y = left, and z = upwards. 
    % Meaning a rotation of 90 degrees around the x-axis. And recalculate from
    % m/s^2 to g's 
    
    R = [0 0 1;
         1 0 0;
         0 -1 0];
    
    data.rotated_gyro_local_pelvis = (R * data.gyro_local_pelvis')';
    data.rotated_acc_local_pelvis = (R * data.acc_local_pelvis')';
    
    data.rotated_gyro_local_Rshank = (R * data.gyro_local_Rshank')';
    data.rotated_acc_local_Rshank = (R * data.acc_local_Rshank')';
    
    data.rotated_gyro_local_Lshank = (R * data.gyro_local_Lshank')';
    data.rotated_acc_local_Lshank = (R * data.acc_local_Lshank')';
    
    % Data
    % - Matrix with each row corresponding to a single frame and...
    %   - Column 1 -- Time stamps (in ms)
    %   - Columns 2:4 -- Linear acceleration x, y, and z in g (~9.81 m/s^2 depending on location data were collected)
    %   - Columns 5:7 -- Angular velocity x, y, and z in rad/s
    X_pelvis = [table2array(df(:, "time")), data.rotated_acc_local_pelvis./9.81, data.rotated_gyro_local_pelvis];
    X_Rshank = [table2array(df(:, "time")), data.rotated_acc_local_Rshank./9.81, data.rotated_gyro_local_Rshank];
    X_Lshank = [table2array(df(:, "time")), data.rotated_acc_local_Lshank./9.81, data.rotated_gyro_local_Lshank];
    
    data.X_pelvis = X_pelvis;
    data.X_Rshank = X_Rshank;
    data.X_Lshank = X_Lshank;

end