#!/bin/sh
mkdir reports/
echo 'Generate statistics of Wildfires and datasets'
python code/plot_data/describe_wfs.py -i gps/ -a data/analysis/ -e data/espanaenllamas/EspanaEnLlamas.csv -w  data/espanaenllamas/wfs.csv -o reports/
echo 'Network analysis plots'
python code/plot_data/network_analysis.py -i data/analysis/ -o reports/
echo 'Simulation result plots'
python code/plot_data/simulations_analysis.py -s data/simulations/ -a data/analysis/ -o reports/
