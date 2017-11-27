#!/bin/bash
mkdir data/interpolated
echo 'Interpolate positions every 30 seconds'
python code/prepare_traces/interpolate_wfs.py  -i gps/ -o data/interpolated
