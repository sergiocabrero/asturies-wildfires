import matplotlib
import os

class Report:
    def __init__(self, title, report_path, figures_folder='./figures'):
        # Open output file
        self.mdfile = open(report_path, 'w+')

        # Setup folder for figures
        self.figures_relpath = figures_folder
        self.figures_abspath = os.path.join(os.path.abspath(os.path.dirname(report_path)), self.figures_relpath)
        if not os.path.exists(self.figures_abspath):
            os.makedirs(self.figures_abspath)

        # Print title
        self.print_line('# %s' % title)

        # Use type 1 fonts in PDFs
        matplotlib.rcParams['ps.useafm'] = True
        matplotlib.rcParams['pdf.use14corefonts'] = True
        matplotlib.rcParams['text.usetex'] = True


    def print_line(self, text):
        self.mdfile.write(text+'\n\n')


    def print_figure(self, fig, name, description):
        # For paper
        fig.savefig('%s/%s.pdf' % (self.figures_abspath, name), bbox_inches='tight')

        self.print_line('#### Figure: %s \n\n' % description)
        # For MD Report
        fig.savefig('%s/%s.png' % (self.figures_abspath, name), bbox_inches='tight')
        self.print_line('![%s](%s/%s.png)\n\n' %(description, self.figures_relpath, name))
        return

    def print_table_from_series(self, series):
        return self.print_table_from_df(series.reset_index())

    def print_table_from_df(self, df):
        import pandas as pd
        fmt = ['---' for i in range(len(df.columns))]
        df_fmt = pd.DataFrame([fmt], columns=df.columns)
        df_formatted = pd.concat([df_fmt, df])
        self.print_line(df_formatted.to_csv(sep="|", index=False))
