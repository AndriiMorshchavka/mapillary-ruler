% Load Data from Specific Worksheet Starting from the Second Row
clear all;
pos = 1;
projectPath =  fileparts(mfilename('fullpath'));
% Define your Python script path
filename = fullfile(projectPath, 'matlab_table.xlsx');
sheetName = 'matlab_input_all';
data = readtable(filename, 'Sheet', sheetName, 'Range', 'A2:X379');

% Set number of iterations and net parameters
num_rep = 10;
testPerformances = zeros (num_rep*3,1);
% Split Data into Training, Validation, and Test Sets
trainRatio = 0.7;
valRatio = 0.15;
testRatio = 0.15;
% Set lambda
lambda = 1;
lvl = 0.25;

% Calculate the number of samples
numSamples = height(data);

% Determine the split indices
numTrain = round(trainRatio * numSamples);
numVal = round(valRatio * numSamples);
numTest = numSamples - numTrain - numVal;

% Convert table to array
inputs = table2array(data(:, [3:6,12,15:22]));%inputVars);
outputs = table2array(data(:, 24));%outputVar);


%% Set regularization parameters
%net.performParam.regularization = lambda;
trainfcnlst = {...
   'trainlm', ...Levenberg-Marquardt
   'trainbr', ...	Bayesian Regularization
   'trainrp', ...	Resilient Backpropagation
   'trainscg', ...	Scaled Conjugate Gradient
   'trainbfg', ...	BFGS Quasi-Newton
   'traincgb', ... Conjugate Gradient with Powell/Beale Restarts
   'traincgf', ...	Fletcher-Powell Conjugate Gradient
   'traincgp', ...	Polak-Ribiére Conjugate Gradient
   'trainoss', ...	One Step Secant
   'traingdx', ...	Variable Learning Rate Gradient Descent
   'traingdm', ...	Gradient Descent with Momentum
   'traingd' ...Gradient Descent
    } ;

for iter=1:1
    hiddenLayerList (iter) = 10;
end

% performance_array = zeros(num_iterations, 2);


for r=1:num_rep
    close all;
    % Generate a random permutation of the row indices
    indices = randperm(numSamples);

    % Determine indices according to data split
    trainIdx = indices(1:numTrain);
    valIdx = indices(numTrain + 1:numTrain + numVal);
    testIdx = indices(numTrain + numVal + 1:end);

    % Create training, validation, and test sets
    trainInputs = inputs(trainIdx, :)';
    trainTargets = outputs(trainIdx)';
    valInputs = inputs(valIdx, :)';
    valTargets = outputs(valIdx)';
    testInputs = inputs(testIdx, :)';
    testTargets = outputs(testIdx)';
    fprintf(['Shuffling', num2str(r), '\n'] );
    
    for i = 1:length(trainfcnlst)
        trainFcnName = trainfcnlst{i};
        fprintf('| %s\t|', trainFcnName);
        for h=1:length(hiddenLayerList)
            hiddenLayerSize = hiddenLayerList(h);
            % Create and Train the Neural Network
            net = feedforwardnet(hiddenLayerSize, 'trainFcn',trainFcnName);

            % Set up division of data for training, validation, and testing
            net.divideFcn = 'divideind';
            net.divideParam.trainInd = trainIdx;
            net.divideParam.valInd = valIdx;
            net.divideParam.testInd = testIdx;
            net.trainParam.showWindow = 0; 
            %view(net)

            % Transpose the full input and output arrays for training
            inputs_transp = inputs';
            outputs_transp = outputs';

            % Train the network
            [net, tr] = train(net, inputs_transp, outputs_transp);
            nets{i,h} = net;
            trs{i,h} = tr;
            % Evaluate the Neural Network
            if ~isempty(tr)
                fprintf(' %.1e\t', tr.best_perf);
                fprintf('%.1e\t', tr.best_vperf);
                if isnan(tr.best_vperf), fprintf('\t'); end
                tblrestest(i,h)=tr.best_tperf;
                fprintf('%.1e\t|', tr.best_tperf);
                testPerformances(pos,1)=tr.best_tperf;
                pos = pos + 1;
                % Optionally plot performance if the last training performance is less than a threshold
            else
                fprintf('Performance is not available\t|');
            end

        end
    fprintf('\n');
    end
    fprintf([' -----------------------------------------------------------------------------------------------\n'] );
    [v,i] = min(min(tblrestest,[],2));
    trainFcnName = trainfcnlst{i};
    [v,h] = min(tblrestest(i,:));
    hiddenLayerSize = hiddenLayerList(h);
    fprintf('the best perf %f achieved for training method (%s) with %d hidden layers \n', v, trainFcnName, hiddenLayerSize);
    fprintf(' -----------------------------------------------------------------------------------------------\n' );

    net = nets{i,h};
    tr = trs{i,h};
    % view(net)
    % plottrainstate(tr)
    % plotperform(tr)

    % Calculate RMSE and MAE on the training set
    trainOutputs = net (trainInputs);
    rmseTrain = rmse (trainTargets, trainOutputs);
    disp ("Training peformance (RMSE): " + string(rmseTrain));    
    maeTrain = mae (trainTargets, trainOutputs);
    disp ("Training peformance (MAE): " + string(maeTrain));

    % Calculate RMSE and MAE on the validation set
    valOutputs = net(valInputs);
    rmseVal = rmse (valTargets, valOutputs);
    disp ("Validation peformance (RMSE): " + string(rmseTrain)); 
    maeVal = mae (trainTargets, trainOutputs);
    disp ("Validation peformance (MAE): " + string(maeTrain));

    % Calculate RMSE and MAE on the test set
    testOutputs = net(testInputs);
    rmseTest = rmse (testTargets, testOutputs);
    disp ("Test peformance (RMSE): " + string(rmseTest)); 
    maeTest = mae (testTargets, testOutputs);
    disp ("Test peformance (MAE): " + string(maeTest));
end
