import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import time
import argparse
from report import Report

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['font.size'] = 6

# %matplotlib inline

def wf_stats(fpath, fname, eell, incidents):
    wf = pd.read_csv(fpath+'/'+fname, index_col=0)

    code = fname.split('_')[0]
    incident = incidents[incidents.Code == code].iloc[0].to_dict()
    eell_report = eell[eell.IDPIF == incident['Name']].iloc[0].to_dict()

    # Merge stats
    stats = {
        'code': code,
        'sample_duration': wf.index.max() - wf.index.min(),
        'controlled_duration': eell_report['TIME_CTRL'],
        'extinguish_duration': eell_report['TIME_EXT'],
        'staff': eell_report['PERSONAL'],
        'nnodes': len(wf.Node.unique()),
        'samples': wf.shape[0],
        'burned': eell_report['SUPQUEMADA'],
        'start_date': incident['Start']

    }
    return stats

def load_data(gpspath, eell_file, incidents_file):
    eell = pd.read_csv(eell_file)
    incidents = pd.read_csv(incidents_file)


    fpath = gpspath
    fnames = [f for f in os.listdir(fpath)]
    process = lambda fname: wf_stats(fpath, fname, eell, incidents)
    stats = map(process, fnames)

    stats_df = pd.DataFrame(stats)
    stats_df.loc[:, 'expected_samples'] = stats_df['nnodes']*stats_df['sample_duration']/30
    return stats_df

def print_stats(stats_df, report):
    report.print_line("## Statistics")
    report.print_line("### Describe/Summary")
    report.print_table_from_df(stats_df.describe())
    report.print_line("### Full Stats")
    report.print_table_from_df(stats_df)

def dataset_scatter(stats_df, report):
    fig = plt.figure(figsize=(7,1.2))
    ax = fig.add_subplot(111)
    stats_df.loc[:, 'Ratio of missed GPS samples'] = (1 - stats_df['samples']/stats_df['expected_samples'])
    stats_df.plot.scatter(ax=ax, y='nnodes', x='samples', c='Ratio of missed GPS samples')
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    ax.set_xlabel('Number of GPS samples in dataset')
    ax.set_ylabel('Number of nodes')

    report.print_figure(fig, 'dataset_scatter_simple', 'Dataset Statistics')


def summary_hist(stats_df, report):
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(7,1.2))
    stats_df['burned'].hist(ax=axes[0], bins=30)
    axes[0].set_xlim(xmin=0)
    axes[0].set_ylim(0,6)
    axes[0].set_ylabel('Wildfires')
    axes[0].set_title('Hectares burned')

    (stats_df['extinguish_duration']/60).hist(ax=axes[1], bins=30)
    axes[1].set_title('Hours until extintion')
    axes[1].set_ylim(0,6)

    (stats_df['samples']/1000).hist(ax=axes[2], bins=30)
    axes[2].set_title('Thousands of samples')
    axes[2].set_ylim(0,6)

    stats_df['nnodes'].hist(ax=axes[3], bins=30)
    axes[3].set_title('Number of nodes')
    axes[3].set_ylim(0,6)

    report.print_figure(fig, 'dataset_hists', 'Dataset Statistics')

def summary_scatter(stats_df, report):
    fig = plt.figure(figsize=(3.5,1.2))
    ax = fig.add_subplot(111)
    stats_df.plot.scatter(ax=ax, y='staff', x='burned', s=stats_df['extinguish_duration']/60, c=stats_df['samples'])
    ax.set_xlim(xmin=0)
    ax.set_ylim(ymin=0)
    ax.set_xlabel('Hectares burned')
    ax.set_ylabel('Staff movilized (according to report)')

    ax.set_title('Dataset summary (size: time for extintion, color: number of samples in dataset)')
    report.print_figure(fig, 'dataset_scatter', 'Dataset Statistics')

def wf_teaser_figure_lines(stats_df, report):
    date_labels = ['Oct 2011', 'Jan 2012', 'Apr 2012', 'Jul 2012', 'Oct 2012']
    date_ticks = map(lambda d: time.mktime(time.strptime(d, '%b %Y')), date_labels)

    fig = plt.figure(figsize=(7,1.5))
    ax = fig.add_subplot(111)
    ax.vlines(stats_df['start_date'], stats_df['burned'], stats_df['burned']+stats_df['extinguish_duration']/60, linewidth=2, color='blue', alpha=0.7)
    # ax.scatter(x=stats_df['start_date'], y=stats_df['burned'], s=stats_df['extinguish_duration']/60)
    ax.set_xticks(date_ticks)
    ax.set_xticklabels(date_labels, rotation=45)
    ax.set_ylim(ymin=0)
    ax.set_xlim(date_ticks[0], date_ticks[-1])
    report.print_figure(fig, 'wf_teaser', 'Wildfires (> 100ha) in Asturias from Oct. 2011 to Oct. 2012')

def wf_teaser_figure_scatterplot(stats_df, report):
    date_labels = ['Oct 2011', 'Jan 2012', 'Apr 2012', 'Jul 2012', 'Oct 2012']
    date_ticks = map(lambda d: time.mktime(time.strptime(d, '%b %Y')), date_labels)
    stats_df.loc[:,'Hours until extinted'] = (stats_df['extinguish_duration']/60).astype('int')

    fig = plt.figure(figsize=(7,1.2))
    ax = fig.add_subplot(111)
    stats_df.plot.scatter(y='start_date', x='burned', c='Hours until extinted', ax=ax, marker='v', s=20, colormap='Reds', edgecolors='black', alpha=0.5)
    ax.set_yticks(date_ticks)
    ax.set_yticklabels(date_labels, rotation=45)
    ax.set_xlim(xmin=0)
    ax.set_ylim(date_ticks[0], date_ticks[-1])
    ax.set_xlabel('Burned surface [ha]')
    ax.set_ylabel('Starting date')

    report.print_figure(fig, 'wf_teaser_scatter', 'Wildfires (> 100ha) in Asturias from Oct. 2011 to Oct. 2012')


if __name__=='__main__':
    argparser = argparse.ArgumentParser(description='This script computes and plots statistics for wildfires and dataset')
    argparser.add_argument('-i', help='Folder with input GPS traces of wildfires', dest='input', required=True)
    argparser.add_argument('-a', help='Folder to output analysis data (wf_stats.csv)', dest='analysis', required=True)

    argparser.add_argument('-e', help='File with data from Espana en Llamas', dest='eell', required=True)
    argparser.add_argument('-w', help='File with Wildfire descriptions', dest='wf', required=True)
    argparser.add_argument('-o', help='Folder for output datasets', dest='output', required=True)


    args = argparser.parse_args()
    ###

    report = Report('Dataset description', '%s/dataset_stats.md' % args.output)
    df = load_data(args.input, args.eell, args.wf)
    df.to_csv(args.analysis+'wf_stats.csv', index=False)
    print_stats(df, report)
    summary_hist(df, report)
    summary_scatter(df, report)
    wf_teaser_figure_lines(df,report)
    wf_teaser_figure_scatterplot(df,report)
    dataset_scatter(df,report)
