from shapely.geometry import Point
from shapely.ops import cascaded_union
import os
import pandas as pd
from geopy.distance import distance as geo_distance
import argparse

def rel_latitude(lat, ref_loc):
    sign = 1 if lat >ref_loc[0] else -1
    return sign*geo_distance(ref_loc,(lat, ref_loc[1])).meters


def rel_longitude(lon, ref_loc):
    sign = 1 if lon > ref_loc[1] else -1
    return sign*geo_distance(ref_loc,(ref_loc[0], lon)).meters

def to_vector(df):
    str_vector = lambda str: (float(str.split(',')[0][1:]), float(str.split(',')[1][:-1]))
    return df.applymap(str_vector)

def to_meters(df, ref):
    rel_position = lambda pos: (rel_latitude(pos[0], ref), rel_longitude(pos[1], ref))
    return df.applymap(rel_position)

def coverage(positions, range, wf_radius = 1000):
    circles = [Point(*c).buffer(range) for c in positions]
    union = cascaded_union(circles)
    wf_surface = Point(0,0).buffer(wf_radius) # 1 km around
    intersection = wf_surface.intersection(union)
    return intersection.area/wf_surface.area

def calulate_coverage(df):
    ranges = [50, 200, 1000]
    series = map(lambda rang: df.apply(lambda row: coverage(row, rang), axis=1), ranges)
    return pd.DataFrame(dict(zip(ranges,series))).unstack('range').rename('area').reset_index().rename(columns={'level_0': 'range'})

def add_names(df, name):
    df.loc[:, 'scenario'] = name
    return df

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='This script calculates the coverage offered by a network infrastructure with antennas located in the nodes')
    argparser.add_argument('-i', help='Folder with input GPS interpolated', dest='interpolated', required=True)
    argparser.add_argument('-w', help='File with wildfire data (Espana En Llamas)', dest='eel', required=True)
    argparser.add_argument('-o', help='Output file', dest='output', default='30s')
    # argparser.add_argument('-r', help='Radius of the area around the wildfire to consider', dest='radius', default='1000')

    args = argparser.parse_args()

    # Load data
    interpolated_path = args.interpolated
    interpolated_fn = os.listdir(interpolated_path)
    names = [f.split('_')[2] for f in interpolated_fn]

    dfs_gps = [pd.read_csv('%s/%s' % (interpolated_path, f), index_col='time') for f in interpolated_fn]


    # Load wf locations
    fn_wf = args.eel
    df_wfs = pd.read_csv(fn_wf)
    wf_locations = df_wfs.groupby('Code').apply(lambda row: (row['Latitude'].iloc[0], row['Longitude'].iloc[0]))


    # Adjust format (reads vectors as strings)
    dfs_gps = map(to_vector, dfs_gps)

    # GPS to meters, taking as reference the reported location of the wildfire
    dfs_meters = map(lambda v: to_meters(v[0], wf_locations[v[1]]), zip(dfs_gps, names))

    # Calculate coverage
    dfs_coverages = map(calulate_coverage, dfs_meters)

    df_coverage = pd.concat(map(lambda v: add_names(*v), zip(dfs_coverages, names)))
    df_coverage.to_csv(args.output, index=False)
