#!/bin/sh
mkdir data/analysis
echo 'Calculate distances and contacts'
python code/analyse_traces/distances.py -i data/interpolated/ -o data/analysis/
echo 'Calculate distances and contacts'
echo 'Social Network Analysis (this may take a while)'
python code/analyse_traces/sna_analysis.py  -i data/analysis/distances/ -o data/analysis/
echo 'Coverage'
python code/analyse_traces/coverage.py -i data/interpolated/ -w data/espanaenllamas/wfs.csv -o data/analysis/coverage_1km.csv
