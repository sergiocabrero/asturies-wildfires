import argparse
import pandas as pd
from geopy.distance import distance
from itertools import combinations
import os

# %matplotlib inline
#
# def walked_distance(wf):
#     f = lambda col: pd.Series(map(lambda a,b: distance(a,b).meters, col.iloc[1:], col.iloc[:-1]))
#     return wf.apply(f)
#
# walked_distances = walked_distance(wf).set_index(wf.index[:-1])
#
# walked_distances.plot(legend=False)
#
# # Speeds in kmh
# ((walked_distances/30)/3.6).plot(legend=False)

def correlate_distance(wf):
    f = lambda cols: pd.Series(wf.loc[:,cols].apply(lambda row: distance(row[0],row[1]).meters, axis=1), index=wf.index)
    col_pairs = list(combinations(wf.columns,2))
    return pd.DataFrame(map(f, col_pairs), index=col_pairs).T

def count_contacts(wf):
    ranges = range(0,1010,20)
    contacts = map(lambda r: 1. * wf[wf < r].count().sum(), ranges)
    return pd.Series(contacts, index=ranges)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='This script calculates distances between nodes and computes the number of contacts vs range')
    argparser.add_argument('-i', help='Folder with input GPS interpolated', dest='input', required=True)
    argparser.add_argument('-o', help='Folder for output datasets', dest='output', required=True)

    args = argparser.parse_args()

    fnames = [f for f in os.listdir(args.input)]

    contacts = {}

    distancespath = args.output+'/distances/'
    if not os.path.exists(distancespath):
        os.makedirs(distancespath)


    for fn in fnames:
        code = fn.split('_')[-3]
        print code
        distances = correlate_distance(pd.read_csv(args.input+'/'+fn, index_col=0))
        distances.to_csv('%s/distance_%s.csv' % (distancespath,code), index_label='time')
        contacts[code] = count_contacts(distances)

    contacts_df = pd.DataFrame(contacts)
    contacts_df.to_csv('%s/contacts_vs_range.csv' % args.output, index_label='range(m)')
