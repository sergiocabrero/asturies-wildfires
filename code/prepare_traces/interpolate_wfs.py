"""
    Input files fomat is: Time(in epoch seconds),Node,Latitude,Longitude
"""
import argparse
import os
import pandas as pd
from datetime import datetime

def date2epoch(date):
    epoch = datetime(1970,1,1)
    return (date - epoch).total_seconds()


def process(inputfolder, inputfile, out_gps, freq):
    wf = pd.read_csv(inputfolder+'/'+inputfile)
    pv = interpolate(wf, freq)
    # Store interpolated GPS
    pv.to_csv('%s/interpolated_%s_%s.csv' % (out_gps, freq, inputfile.split('.')[0]), index_label='time')

def interpolate(wf, freq):
    wf.Time = pd.to_datetime(wf.Time*10**9)
    wf.loc[:, 'Position'] = pd.Series(zip(wf.Latitude, wf.Longitude))
    pv = wf.pivot_table(values='Position', columns='Node', index='Time', aggfunc=lambda x: x.iloc[-1]).fillna(method='ffill').fillna(method='bfill')
    pv = pv.asfreq(freq).fillna(method='ffill').fillna(method='bfill')
    pv = pv.set_index(pv.index.to_series().apply(date2epoch))
    return pv

# def remove_outliers(df):
#     wf = df
#     f = lambda col: map(lambda a,b: distance(a,b).meters, col[1:], col[:-1])
#     distances = wf.groupby('Node').Position.transform(f)
#     wf.loc[:,'ts'] = wf.Time.dt.apply(date2epoch)
#     interval = wf.groupby('Node').ts.transform(lambda col: col.values[1:]-col.values[:-1])

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='This script uses a GPS traces file and a Wildfires (Scenarios) filter file to create GPS traces and anonymize GPS traces')
    argparser.add_argument('-i', help='Folder with input GPS', dest='input', required=True)
    argparser.add_argument('-o', help='Folder for interpolated GPS output files', dest='output', required=True)
    argparser.add_argument('-f', help='Interpolation frequency', dest='freq', default='30s')

    args = argparser.parse_args()

    files = [f for f in os.listdir(args.input)]

    mymap = lambda x: process(args.input, x, args.output, args.freq)
    map(mymap, files)
