function changePoints = detectModeChanges(labels)


    labels.walk_mode = categorical(labels.walk_mode);
    walk_modes = labels.walk_mode;
    changePoints = find(~strcmp(walk_modes(1:end-1), walk_modes(2:end))) + 1;

end

