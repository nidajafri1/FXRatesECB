# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 19:22:50 2020

@author: n.jafri
"""
import requests
import pandas as pd
import numpy as np
import os

def fxrates_dict(url):
    '''
    ECB's API on foreign exchange. Run your GET and recieve a json dict of rates
    Read docs: https://exchangeratesapi.io/

    Parameters
    ----------
    url : str
        https://exchangeratesapi.io/ - look on this website for your GET request.

    Returns
    -------
    fxrates_dict : json dictionary
        takes the rates and converts them into a json dictionary.

    '''
    r = requests.get(url)
    fxrates_nesteddict = r.json()
    fxrates_dict = fxrates_nesteddict['rates']
    
    return fxrates_dict

def fxratesdict_df(fxrates_dict):
    '''
    Insert your dict of fx rates and get a cleaned out unstacked/(or pd.melt) 
    normalised df.

    Parameters
    ----------
    fxrates_dict : json dictionary
        obtained in fxrates_dict function.

    Returns
    -------
    fxrates_df : pandas DataFrame
        normalised version of the fx_rates dictionary.

    '''
    fxrates_df = pd.DataFrame.from_dict(fxrates_dict, orient='index')
    fxrates_df = fxrates_df.stack().reset_index() #unpivoting, pd.melt
    fxrates_df.rename(columns={'level_0': 'Date_of_fx_rate', 'level_1': 'ISO_Code', 0:'From'}, inplace=True)

    return fxrates_df

def crossrates_df(fxrates_df):
    '''
    A lot of cleaning to calculate the cross rates at the end of each year.

    Parameters
    ----------
    fxrates_df : pandas DataFrame
        obtained from fxratesdict_df.
    
    Returns
    -------
    fxrates_df : pandas DataFrame
        cross rates calculated in TO and FROM, for each year at 31st Dec.

    '''
    fxrates_df.rename(columns={'level_0': 'Date_of_fx_rate', 'level_1': 'ISO_Code', 0:'From'}, inplace=True) #rename cols
    fxrates_df_temp = pd.DataFrame(fxrates_df) #create a copy df for outer join
    fxrates_df = fxrates_df.merge(fxrates_df_temp, how='outer', left_on='Date_of_fx_rate', right_on='Date_of_fx_rate')
    fxrates_df.rename(columns={'ISO_Code_x': 'ISOCode_From', 'From_x': 'EurotoCurrency1', 'ISO_Code_y': 'ISOCode_To', 'From_y': 'EurotoCurrency2'}, inplace=True)
    
    fxrates_df['From'] = fxrates_df['EurotoCurrency1']/fxrates_df['EurotoCurrency2']
    fxrates_df['To'] = fxrates_df['EurotoCurrency2']/fxrates_df['EurotoCurrency1']
    fxrates_df.drop(columns=['EurotoCurrency1', 'EurotoCurrency2'], inplace=True)
    fxrates_df['Date_of_fx_rate'] = pd.to_datetime(fxrates_df['Date_of_fx_rate'])
        
    fxrates_df = fxrates_df.loc[(fxrates_df['Date_of_fx_rate'].dt.day==np.max(fxrates_df['Date_of_fx_rate'].dt.day)) 
                                    & (fxrates_df['Date_of_fx_rate'].dt.month==np.max(fxrates_df['Date_of_fx_rate'].dt.month))]
    
    return fxrates_df

def to_excel(fxrates_df, filename):
    '''
    Put your fxrates DataFrame into an excel sheet.

    Parameters
    ----------
    fxrates_df : pandas DataFrame
        obtained from crossrates_df.
        
    filename : str
        excel file name. PLEASE PUT IT T THROUGH r'filename.xlsx'

    Returns
    -------
    prints the path where the filename is saved.

    '''
    fxrates_df.to_excel(filename, index=False, header=True)
    
    print('file saved in path {}'.format(os.getcwd()))

fxratesdict = fxrates_dict('https://api.exchangeratesapi.io/history?start_at=2010-01-01&end_at=2020-01-01')
fxratesdicttodf = fxratesdict_df(fxratesdict)
crossratesdf = crossrates_df(fxratesdicttodf)
to_excel(crossratesdf, r'apifxrates.xlsx')
