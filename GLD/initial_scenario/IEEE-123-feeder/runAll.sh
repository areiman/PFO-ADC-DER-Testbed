#!/bin/bash

clear

echo "Executing experiment..."

experimentPath="C:/Users/reim112/Documents/PNNL/GMLC_Control/GLD/model_generation/populationScripts/experiments/IEEE-123-feeder"

cd $experimentPath/IEEE_123_feeder_0 && gridlabd IEEE_123_feeder_0.glm &> simLog.out &

echo "Waiting for processes to finish..."

wait

echo "Done..."

