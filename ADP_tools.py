import numpy as np
from scipy import stats
import pandas as pd
import xarray as xr
import fp_plotting as fpp
from physoce import tseries as ts
import datetime
import os




def t_reader(filename):
    
    dfT = dfT = pd.read_csv(str(filename), delimiter='\s+', names = ["depth", "1", "water_dir", "V_x", "V_y", "V_z", "6", "7", "8", "9", "10", "11", "flag"])
    
    line_end = int(dfT.iloc[5,0])
    line_end = line_end+6
    
    start_time = str(str(int(dfT.iloc[0,0])) + '-' + str(int(dfT.iloc[0,1])) + '-' + str(int(dfT.iloc[0,2]))
                + ' ' + str(int(dfT.iloc[0,3])) + ':' + str(int(dfT.iloc[0,4])) + ':' + str(int(dfT.iloc[0,5])))
    samp_int = str(dfT.iloc[3,2] + 'S')
    times = pd.date_range(str(start_time), periods=int((len(dfT)/line_end)), freq=samp_int)
    
    df1 = dfT.iloc[6:line_end,:]
    df1.insert(0,'longitude',dfT.iloc[3,1])
    df1.insert(0,'latitude',dfT.iloc[3,0])
    df1.insert(0,'date_time',times[0])
    df1.insert(0,'profile', 1)
    for i in range(1, len(df1)):
        if df1.iloc[i,16]>100:
            df1.iloc[i, 7:10] = 'nan'
    for x in range(1, int((len(dfT)/line_end))):
        df2 = dfT.iloc[(6+(line_end*x)):(line_end*(x+1)),:]
        df2.insert(0,'longitude',dfT.iloc[(3+(line_end*x)),1])
        df2.insert(0,'latitude',dfT.iloc[(3+(line_end*x)),0])
        df2.insert(0,'date_time',times[x])
        df2.insert(0,'profile', x+1)
        for y in range(1, len(df2)):
            if df2.iloc[y,16]>100:
                df2.iloc[y, 7:10] = 'nan'
        df1 = df1.append(df2)
    return df1