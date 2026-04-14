function [gyro_local, acc_local] = global2local(gyro_global, acc_global, quat)
%GLOBAL2LOCAL % Rotate sensor data from the global frame to the sensor's local frame
% 
% Parameters:
%   gyro_global: Nx3 matrix of angular velocity (rad/s) in the global frame
%   acc_global: Nx3 matrix of linear acceleration (m/s^2) in the global
%   frame
%   quat: Nx4 matrix of quaternions (w, x, y, z) from the sensor
%
% Returns:
%   gyro_local: Nx3 matrix of angular velocity in the local (sensor) frame
%   acc_local: Nx3 matrix of linear acceleration in the local (sensor)
%   frame

    % Convert quaternion to a quaternion object (MATLAB uses [w, x, y, z] format)
    N = size(gyro_global,1);
    gyro_local = zeros(N,3);
    acc_local = zeros(N,3);


    % for i = 1:N
    %     q = quaternion(quat(i,:)); % Creates an array of quaternion objects
    % 
    %     % Compute the inverse (conjugate) of the quaternion
    %     q_inv = conj(q);
    % 
    %     % Rotate the global gyroscope vector to the local frame
    %     gyro_local(i, :) = rotatepoint(q_inv, gyro_global(i, :));
    %     acc_local(i, :) = rotatepoint(q_inv, acc_global(i, :));
    % end
    
    q = quaternion(quat);  % Convert all quaternions at once
    gyro_local = rotatepoint(conj(q), gyro_global); % Apply inverse rotation in one step
    acc_local = rotatepoint(conj(q), acc_global); 


end

