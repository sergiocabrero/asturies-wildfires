import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from report import Report
import argparse

argparser = argparse.ArgumentParser(description='This scripts plots the results of the simulation')
argparser.add_argument('-o', help='Reports path', dest='report', required=True)
argparser.add_argument('-s', help='Path of the simulation results', dest='input_simulation', required=True)
argparser.add_argument('-a', help='Path of the analysis data', dest='input_analysis', required=True)

args = argparser.parse_args()


""" Set styles """
sns.set_style('white')

""" Report """
reportfile = args.report+'/simulations_analysis.md'
report = Report('Simulations Analysis', reportfile)


""" Load data """
fn_sims = args.input_simulation+'/one_messagestatsreports.csv'
fn_stats = args.input_analysis+'/wf_stats.csv'

df_stats = pd.read_csv(fn_stats, index_col=0)
df_sims = pd.read_csv(fn_sims)
# filter
df_sims = df_sims.loc[df_sims.report == 'MessageStatsReport', :]
# remove _ from column names, seaborn and latex don't like it (this is a hack!)
old_columns = df_sims.columns
new_columns = {c: c.replace('_','') for c in old_columns}
df_sims.rename(columns=new_columns, inplace=True)

# append wf data to results
df_sims.loc[:, 'nnodes'] = df_sims.scenario.map(df_stats.set_index('code').nnodes)
df_sims.loc[:, 'duration'] = df_sims.scenario.map(df_stats.set_index('code').sample_duration)

# calculate bytes sent:
get_bytes = {'1k': 1024, '1M': 1024*1024, '10k': 10*1024, '512k': 512*1024, '128k': 128*1024, '256k': 128*1024}
df_sims.loc[:, 'bytesdelivered'] = df_sims.delivered * df_sims['size'].map(get_bytes)
df_sims.loc[:, 'bytescreated'] = df_sims.created * df_sims['size'].map(get_bytes)

df_sims.loc[:, 'mpbs'] = 8*(df_sims.bytesdelivered) / df_sims.duration / (1024*1024)

# Create categories

df_sims['size'] = df_sims['size'].astype('category', categories=['1k', '10k', '128k', '256k', '512k', '1M'], ordered=True)
df_sims['interval'] = df_sims['interval'].astype('category', categories=['5s', '10s', '30s', '60s'], ordered=True)

# Beautify names
df_sims.rename(columns={'interval': 'Message Interval'}, inplace=True)

df_sims.routing = df_sims.routing.apply(lambda x: x[:-6])
df_sims.buffer = df_sims.buffer.apply(lambda x: '100 MB' if x=='100M' else '7500 KB')

""" Overview """
report.print_line("## Overview")

ax = sns.jointplot(data=df_sims, size=3.5, stat_func=None, gridsize=10,  x='deliveryprob', y='latencyavg', color='k', kind='hex', marginal_kws=dict(bins=10)).set_axis_labels('Delivery Probability', 'Average Latency (seconds)')
report.print_figure(ax.fig, 'delivery_latency_overview', 'Overview of the distributions of latency and delivery probability')

ax = sns.jointplot(data=df_sims, size=3.5, stat_func=None, gridsize=10,  x='deliveryprob', y='hopcountavg', color='k', kind='hex', marginal_kws=dict(bins=10)).set_axis_labels('Delivery Probability', 'Average Hop Count')
report.print_figure(ax.fig, 'delivery_hopcount_overview', 'Overview of the distributions of average hop count and delivery probability')

ax = sns.jointplot(data=df_sims, size=3.5, stat_func=None, gridsize=10,  x='deliveryprob', y='nnodes', color='k', kind='hex', marginal_kws=dict(bins=10)).set_axis_labels('Delivery Probability', 'Average Latency (seconds)')
report.print_figure(ax.fig, 'delivery_nnodes_overview', 'Overview of the distributions of number of nodes and delivery probability')

factors_table = df_sims.pivot_table(index=['buffer', 'routing'], columns=['Message Interval', 'size'], values='deliveryprob')
report.print_table_from_df(factors_table)

""" Scenarios variation """
report.print_line("## Heterogeneity")
fig = plt.figure(figsize=(3.5,3.5))
ax = sns.stripplot(data=df_sims, x='mpbs', y='scenario')
ax.set_yticks([])
ax.set_ylabel('Wildfires')
ax.set_xlabel('Network bitrate (in Mbps)')
ax.set_xlim(0,0.8)

report.print_figure(fig, 'bitrate_wildfires', 'Bitrate obtained in the network inthe different wildfires')

""" System factors """
report.print_line("## System factors")
fig = plt.figure(figsize=(3.5,3.5))
ax = sns.violinplot(data=df_sims, x='deliveryprob', hue='routing', y='buffer', split=True)
ax.set_ylabel('Buffer size')
ax.set_xlabel('Delivery probability')
plt.legend(title='Routing')
ax.set_xlim(0,1)

report.print_figure(fig, 'system_factors', 'Influence of buffer and routing in delivery')
report.print_table_from_series(df_sims.groupby(['routing', 'buffer']).deliveryprob.mean())
report.print_table_from_series(df_sims.groupby(['routing', 'buffer']).mpbs.mean())
report.print_table_from_series(df_sims.groupby(['buffer']).deliveryprob.mean())
report.print_table_from_series(df_sims.groupby(['buffer']).mpbs.mean())
report.print_table_from_series(df_sims.groupby(['routing']).deliveryprob.mean())
report.print_table_from_series(df_sims.groupby(['routing']).mpbs.mean())


""" Workload factors """
report.print_line("## Workload factors")

ax = sns.factorplot(data=df_sims, size=3.5, aspect=1, y='deliveryprob', x='size', col_wrap=2, col='Message Interval', kind='violin').set_axis_labels('Message Size', 'Delivery probability')
plt.ylim(0,1)
report.print_figure(ax.fig, 'workload_factors', 'Influence of message size and interval in delivery')

# Created/Delivered MB
df_sims['mbdelivered'] = df_sims.bytesdelivered / (1024*1024)
df_sims['mbcreated'] = df_sims.bytescreated / (1024*1024)

fig = plt.figure(figsize=(3.5,3.5))
ax = sns.regplot(data=df_sims, y='mbdelivered', x='mbcreated', truncate=True, marker='x', line_kws={'color': 'k'}, scatter_kws={'color': 'b'})
ax = sns.regplot(data=df_sims, y='mbdelivered', x='mbcreated', truncate=True, marker='x', line_kws={'color': 'k'}, scatter_kws={'color': 'b'})

ax.set_xlabel('MegaBytes created')
ax.set_ylabel('MegaBytes delivered')
ax.set_ylim(0, 1.1*max(df_sims.mbdelivered))
ax.set_xlim(0, 1.1*max(df_sims.mbcreated))

report.print_figure(fig, 'bytescreated_delivered', 'Influence of created bytes in delivery')


# Correlations:
df_sims['bsize'] = df_sims['size'].map(get_bytes)
t = df_sims.loc[:, ['bsize', 'deliveryprob']].corr()
report.print_table_from_df(t)

t = df_sims.loc[:, ['bsize', 'latencyavg']].corr()
report.print_table_from_df(t)

df_sims['minterval'] = df_sims['Message Interval'].apply(lambda s: s[:-1]).astype('int')

t = df_sims.loc[:, ['minterval', 'deliveryprob']].corr()
report.print_table_from_df(t)

t = df_sims.loc[:, ['minterval', 'latencyavg']].corr()
report.print_table_from_df(t)
