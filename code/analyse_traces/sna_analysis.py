import pandas as pd
import os
import networkx as nx
import itertools
import argparse

""" help methods """
def get_scenario_name(fname):
    return fname.split('_')[-1][0:-4]

def calculate_contacts(distances_file, rang=200):
    df = pd.read_csv(distances_file, index_col=0)
    return df.applymap(lambda x: 1 if x <= rang else 0)

def get_nodes_from_index(ind):
    return ind.split("'")[1:4:2]

def build_graph(row):
    # this gets just the connected nodes
    G = nx.Graph()
    edges = map(get_nodes_from_index, list(row[row==1].index))
    G.add_edges_from(edges)
    return G

def add_condition(df, condition):
    df['scenario'] = get_scenario_name(condition[0])
    df['range'] = condition[1]
    return df

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='This scripts calculates Social Network Analysis metrics')
    argparser.add_argument('-o', help='Output path', dest='output', required=True)
    argparser.add_argument('-i', help='Path containing distance between nodes during wildfires', dest='distances', required=True)

    args = argparser.parse_args()

    """ Config """
    datapath = args.output
    distancespath = args.distances
    fnames = [distancespath+'/'+f for f in os.listdir(distancespath) if 'WF25' not in f and 'WF19' not in f]
    ranges = [50, 200, 1000]

    """ Prepare data """
    scenarios = map(get_scenario_name, fnames)
    conditions = list(itertools.product(fnames, ranges))
    adj_matrixes = map(lambda v: calculate_contacts(*v), conditions)
    graphs = map(lambda adjm: adjm.apply(build_graph, axis=1), adj_matrixes)

    """ Get degree """
    get_degrees = lambda graphs: graphs.apply(nx.degree).apply(pd.Series).stack().reset_index().rename(columns={0: 'degree', 'level_1': 'node'})
    degrees = map(get_degrees, graphs)
    # merge and save
    pd.concat(map(lambda v: add_condition(*v), zip(degrees, conditions))).to_csv(datapath+'/nodedegree.csv', index=False)

    """ Get partitions """
    partitions = map(lambda df: df.apply(nx.number_connected_components).reset_index().rename(columns={0: 'partitions'}), graphs)
    # merge and save
    pd.concat(map(lambda v: add_condition(*v), zip(partitions, conditions))).to_csv(datapath+'/partitions.csv', index=False)

    """ Get routes """
    def get_routes(df):
        try:
            df = df.apply(nx.shortest_path_length).apply(pd.Series).stack().apply(pd.Series).stack().reset_index()
            df.rename(columns={0: 'route_length', 'level_1': 'node_A', 'level_2': 'node_B'}, inplace=True)
            # Filter
            df = df[df.node_A != df.node_B]
            keys = df.apply(lambda r: min(r.node_A, r.node_B) + '_' + max(r.node_A, r.node_B) + '_' + str(r.time), axis=1)
            df = df[keys.duplicated() == False]
        except:
            print 'Failed'
            print df.head()
            df = pd.DataFrame()
        return df


    routes = map(get_routes, graphs)

    # merge and save
    pd.concat(map(lambda v: add_condition(*v), zip(routes, conditions))).to_csv(datapath+'/route_lengths.csv', index=False)
