import requests
from os import listdir, remove
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date
from zipfile import ZipFile

# ------------------------------------------------------------------------------
# constants
_french_csv = "F-F_Research_Data_Factors.CSV"
_french_zip = "F-F_Research_Data_Factors_CSV.zip"
_french_url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
_first_ym   = 192601 # January of the first year of the data
_data_cols  = ['Mkt-RF','SMB','HML','RF']

# ------------------------------------------------------------------------------
def download_zip(url, save_path, chunk_size=128):
    """wrapper from 'requests' documentation"""
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

# TODO: find more elegant way of writing this
def _to_int(row):
    try:
        return np.int64(row)
    except:
        return 99

# TODO: find more elegant way of writing this
def _to_float(row):
    try:
        return round(np.float64(row),4)
    except:
        return np.nan

# ------------------------------------------------------------------------------
# FamaFrench class
class FamaFrench:

    def __init__(self,start=192607,end=None):

        # Fama French file name
        today = date.today().__str__().replace('-','')[:6]
        ff_file_name = "fama-french-" + today + ".csv"

        # look for Fama French (and download if not found or stale)
        if ff_file_name not in listdir():
            print(ff_file_name + " not found: downloading from internet...")
            try: 
                download_zip(_french_url+_french_zip,_french_zip)
                ZipFile(_french_zip).extract(_french_csv)
            except:
                raise Exception("Couldn't download or unzip " + ff_file_name)

            # load/clean Fama French
            _converters = dict(zip(_data_cols,len(_data_cols)*[_to_float]))
            _converters[0] = _to_int

            try: 

                # load
                self.X = pd.read_csv(
                    _french_csv,
                    header=2,
                    index_col=0,
                    converters = _converters
                )

                # clean-up
                self.X = self.X.dropna()
                remove(_french_csv)
                remove(_french_zip)

            except:
                raise Exception("Couldn't load/clean " + ff_file_name)

            # save file
            self.X.to_csv(ff_file_name)

        else: # if found and not stale, load
            try:
                self.X = pd.read_csv(ff_file_name,index_col=0)
            except:
                raise Exception("Existing file not formatted correctly")

        # split into monthly and annual data sets
        # aliens/cavemen: this won't work for your time periods
        self.Xm = self.X.loc[self.X.index>_first_ym]
        self.Xa = self.X.loc[self.X.index<_first_ym]

    def __str__(self):
        """E[R] and SD[R] for each factor"""
        df = pd.DataFrame([self.Xa.mean(),self.Xa.std()])
        df.index = ['E[R]','SD[R]']
        header = '\nAnnual Returns (%):\n\n'
        return header + df.__str__()

    def get_monthly(self,start=_first_ym):
        """
        Get monthly data and decimalize

        Parameters
        ----------
        start : int
            First YearMonth of returns (e.g. 198001 for Jan. 1980)
        """
        return .01*self.Xm.loc[self.Xm.index>=start] 

    def plot_annual(self,mktrf=True,smb=True,hml=True,start=_first_ym//100):
        """
        Plot value of a USD invested in year 'start' against subsequent years

        Parameters
        ----------
        mktrf : bool
            If True, plots Mkt-RF
        smb : bool
            If True, plots SMB
        hml : bool
            If True, plots HML
        start : int
            Year of initial investment of 1 USD (e.g. 1980)
        """

        # decimalize and compute cumulative returns
        _X = self.Xa.loc[self.Xa.index>=start]
        _X = 1.+.01*_X
        _X = _X.shift(fill_value=1.)
        _X = _X.cumprod()
        
        # plot
        leg = []
        if mktrf:
            leg.append("Ecess Market Return (Mkt-RF)")
            plt.plot(_X.index,_X['Mkt-RF'])
        if smb:
            leg.append("Long Small, Short Big (SMB)")
            plt.plot(_X.index,_X['SMB'])
        if hml:
            leg.append("Long Value, Short Growth (HML)")
            plt.plot(_X.index,_X['HML'])

        # clean-up and show
        plt.plot(_X.index,1.+0.*_X.index,'--k')
        plt.legend(leg)
        plt.ylabel('Value (USD)')
        plt.xlabel('Year')
        plt.title('Value of 1 USD invested in ' + str(start))
        plt.grid()
        plt.show()

FF = FamaFrench()
