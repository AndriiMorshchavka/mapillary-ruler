clear all
projectPath =  fileparts(mfilename('fullpath'));

% % Define your Python script path
pythonScript = fullfile(projectPath, '__py_cache__\python_script.cpython-311.pyc');

% Load the saved neural network
netFileAll = fullfile(projectPath, 'nets_report\net_test_report.mat');
netFileStefanhrt = fullfile(projectPath, 'nets_report\net_mit_stefanhrt_test_report.mat');
loadedDataAll = load(netFileAll);
loadedDataStefanhrt = load (netFileStefanhrt);
netAll = loadedDataAll.net;
netStefanhrt = loadedDataStefanhrt.net;

for i=1:100000
    % % Call Python script and capture output
    [status, pythonOutput] = system(['python ', pythonScript]);
    
    inputString = strsplit (pythonOutput, ',');
    disp(pythonOutput);

    inputNumAll = str2double (inputString (:, 4:16));    
    inputNetAll = inputNumAll (:, 1:13);
    inputNetTransAll = inputNetAll';

    inputNumStefanhrt = str2double (inputString (:, 6:16));    
    inputNetStefanhrt = inputNumStefanhrt (:, 1:11);
    inputNetTransStefanhrt = inputNetStefanhrt';

    
    % Get net output
    outputAll = netAll(inputNetTransAll);
    disp (num2str (outputAll));
    outputStefanhrt = netStefanhrt (inputNetTransStefanhrt);
    disp (num2str (outputStefanhrt));
    
    % Create the formatted message string
    message = sprintf(['Approximate building height (net for all): %.1f m\n' ...
        'Approximate building height (net for stefanhrt); %.1f m)'], outputAll, outputStefanhrt);
    msgbox (message);
end