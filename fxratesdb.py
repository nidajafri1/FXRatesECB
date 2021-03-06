# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 00:06:21 2020

@author: n.jafri

"""
import pandas as pd
import numpy as np
import os
import re

def crossrates_df(excelfilexlsx, frequencytype, seriestype):
    '''
    Calculate cross rates for December of each year in ECB's database. Two rate types: 1) Average Daily spot Rate at 31st Dec 2) Average Annual rate for period Jan-Dec.
    Parameters
    ----------
    excelfilexlsx : str
        excel file name.
    frequencytype : str
        'A (Annual)'== for annual averages.
        'D (Daily)'== for annual spot rates.
    seriestype : str
        'A (Average)'== for average of frequency. PICK THIS FOR BOTH RATE TYPES.
        'E (End-of-period)'== for end of period spot rate.
        
    Returns
    -------
    ratedf : pandas DataFrame
        cross rates between Currency_To and Currency_From, with frequency, series type and time period.

    '''
    
    ecbfxrates = pd.read_excel(excelfilexlsx, index_col=None)
    
    ratedf = ecbfxrates.loc[(ecbfxrates['Frequency']==frequencytype) & (ecbfxrates['Series variation - EXR context']==seriestype)]
    ratedf['Year'] = ratedf['Time period or range'].dt.year
    ratedf = ratedf.loc[ratedf.groupby(['Year', 'Currency'])['Time period or range'].idxmax()]
    
    #remove unneccessary columns
    ratedf = ratedf[['Frequency', 'Currency', 'Series variation - EXR context', 'Time period or range', 'Observation value']].copy()
        
    #temp copy of df for outer join
    ratedftemp = ratedf.copy()
    
    ratedf = ratedf.merge(ratedftemp, how='outer', left_on='Time period or range', right_on='Time period or range')
    
    ratedf = ratedf[ratedf['Observation value_x'].notna()]
    
    ratedf['From'] = ratedf['Observation value_x']/ratedf['Observation value_y']
    ratedf['To'] = ratedf['Observation value_y']/ratedf['Observation value_x']
    
    ratedf.drop(columns={'Observation value_x', 'Observation value_y', 'Frequency_y', 'Series variation - EXR context_y'}, inplace=True)
    ratedf.rename(columns={'Currency_x': 'Currency_To', 'Currency_y': 'Currency_From', 'Frequency_x': 'Frequency', 'Series variation - EXR context_x': 'Series variation - EXR context'}, inplace=True)
               
    return ratedf
    
def joincrossrates_df(spotratedf, averagedf):
    '''
    After returning two DataFrames from crossrates_df with different rate types, use this function to union or concatenate them.
    
    Parameters
    ----------
    spotratedf : pandas DataFrame
        DataFrame of cross rates for rate type annual average spot rate.
    averagedf : pandas DataFrame
        DataFrame of cross rates for rate type annual average rate.

    Returns
    -------
    result_df : pandas DataFrame
        DataFrame with combined .

    '''
    spotratedf['Rate Type'] = 'Spot Rate Average' #rate types specified before union
    averagedf['Rate Type'] = 'Annual Average'
    
    #ISO Codes in one column and description in another column
    averagedf['Currency_To_Description'] = averagedf['Currency_To'].str.replace(r'[^(]*\(|\)[^)]*', '')
    spotratedf['Currency_To_Description'] = spotratedf['Currency_To'].str.replace(r'[^(]*\(|\)[^)]*', '')
    averagedf['Currency_To'] = averagedf['Currency_To'].astype(str).str[:3]
    spotratedf['Currency_To'] = spotratedf['Currency_To'].astype(str).str[:3]
    
    averagedf['Currency_From_Description'] = averagedf['Currency_From'].str.replace(r'[^(]*\(|\)[^)]*', '')
    spotratedf['Currency_From_Description'] = spotratedf['Currency_From'].str.replace(r'[^(]*\(|\)[^)]*', '')
    averagedf['Currency_From'] = averagedf['Currency_From'].astype(str).str[:3]
    spotratedf['Currency_From'] = spotratedf['Currency_From'].astype(str).str[:3]
         
    averagedf = averagedf[['Rate Type', 'Frequency', 'Series variation - EXR context', 'Time period or range',
                  'Currency_To', 'Currency_To_Description', 'Currency_From', 'Currency_From_Description',
                  'To', 'From']].copy()
    
    spotratedf = spotratedf[['Rate Type', 'Frequency', 'Series variation - EXR context', 'Time period or range',
                  'Currency_To', 'Currency_To_Description', 'Currency_From', 'Currency_From_Description',
                  'To', 'From']].copy()
    
    frames = [spotratedf, averagedf]
    result_df = pd.concat(frames)
    
    return result_df

def savetoexcel_df(result_df, filenamexlsx):
    '''
    Save pandas DataFrame from either crossrates_df or joincrossrates_df into excel.

    Parameters
    ----------
    result_df : pandas DataFrame
    filename: str,
        r'filname.xlsx' -- put argument through as such.
        
    Returns
    -------
    prints path of where the Excel file is saved.

    '''
    result_df.to_excel(filenamexlsx, index=False, header=True, sheet_name='fx rates data')
    
    print('Saved in path: {}'.format(os.getcwd()))
