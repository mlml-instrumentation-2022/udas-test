from scipy import stats
import numpy as np
import pandas as pd
import xarray as xr
import datetime
import os
import math

#=============================================== T file functions =====================================================================================================
def t_reader(filename):

    """
    Rearanges .T files into a more user friendly format with labelled columns and depth-binned velocities. Creates the basic dataframe file used
    for other ADP_tools functions.

    REQUIREMENTS AND CONSIDERATIONS
    - .T file converted into space deliniated .csv files
    - ADP heading is based on XYZ coordinate system, if another coordinate system (ENU or BEAM) is used you may have to alter some of the code

    INPUTS
    - filename of .T file converted into read_csv

    OUTPUTS
    - t_reader dataframe that can be saved as .csv
    """
    dfT = dfT = pd.read_csv(str(filename), delimiter='\s+', names = ["Bin_depth", "V", "Water_dir", "V_x", "V_y", "V_z", "6", "7", "8", "9", "10", "11", "Flag"])

    line_end = int(dfT.iloc[5,0])
    line_end = line_end+6

    start_time = str(str(int(dfT.iloc[0,0])) + '-' + str(int(dfT.iloc[0,1])) + '-' + str(int(dfT.iloc[0,2]))
                + ' ' + str(int(dfT.iloc[0,3])) + ':' + str(int(dfT.iloc[0,4])) + ':' + str(int(dfT.iloc[0,5])))
    samp_int = str(dfT.iloc[3,2] + 'S')
    times = pd.date_range(str(start_time), periods=int((len(dfT)/line_end)), freq=samp_int)
    dfT["V"] = pd.to_numeric(dfT["V"], errors = "coerce", downcast="float")
    dfT['V'] = dfT['V']/100
    dfT["V_x"] = pd.to_numeric(dfT["V_x"], errors = "coerce", downcast="float")
    dfT['V_x'] = dfT['V_x']/100
    dfT["V_y"] = pd.to_numeric(dfT["V_y"], errors = "coerce", downcast="float")
    dfT['V_y'] = dfT['V_y']/100
    dfT["V_z"] = pd.to_numeric(dfT["V_z"], errors = "coerce", downcast="float")
    dfT['V_z'] = dfT['V_z']/100

    df1 = dfT.iloc[6:line_end,:]
    df1.insert(2,'ADP_heading',dfT.iloc[0,11])
    df1.insert(0,'Avg_depth', np.mean(dfT.iloc[1,8:11]))
    df1.insert(0,'Delta_DMG',dfT.iloc[2,4])
    df1.insert(0,'Longitude',dfT.iloc[3,1])
    df1.insert(0,'Latitude',dfT.iloc[3,0])
    df1.insert(0,'Date_time',times[0])
    df1.insert(0,'Profile', 1)
    for i in range(1, len(df1)):
        if df1.iloc[i,19]>100:
            df1.iloc[i, 7:14] = 'nan'
    for x in range(1, int((len(dfT)/line_end))):
        df2 = dfT.iloc[(6+(line_end*x)):(line_end*(x+1)),:]
        df2.insert(2,'ADP_heading',dfT.iloc[((line_end*x)),11])
        df2.insert(0,'Avg_depth',np.mean(dfT.iloc[1+(line_end*x),8:11]))
        df2.insert(0,'Delta_DMG',((dfT.iloc[(2+(line_end*x)),4]) - (dfT.iloc[(2+(line_end*(x-1))),4])))
        df2.insert(0,'Longitude',dfT.iloc[(3+(line_end*x)),1])
        df2.insert(0,'Latitude',dfT.iloc[(3+(line_end*x)),0])
        df2.insert(0,'Date_time',times[x])
        df2.insert(0,'Profile', x+1)
        for y in range(1, len(df2)):
            if df2.iloc[y,19]>100:
                df2.iloc[y, 7:14] = 'nan'
        df1 = df1.append(df2)
    df1 = pd.DataFrame(df1, columns=['Profile', 'Date_time', 'Latitude', 'Longitude', 'Delta_DMG','Avg_depth', 'Bin_depth',
                                     'V', 'ADP_heading', 'Water_dir', 'V_x', 'V_y', 'V_z', 'Flag'])
    df1 = df1.astype({'Latitude':'float','Longitude':'float','Delta_DMG':'float','Avg_depth':'float','Bin_depth':'float',
                    'V':'float','ADP_heading':'float','Water_dir':'float','V_x':'float','V_y':'float','V_z':'float','Flag':'float'})
    df1['Longitude'] = df1['Longitude']*100
    df1['Delta_DMG'] = df1['Delta_DMG']*100
    return df1

def T_transect_bearing(dfT):
    """
    Calculates the bearing between two points.
    Uses modified .T files from T_reader
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """

    lat1 = math.radians(np.float(dfT.iloc[0,2]))
    lat2 = math.radians(np.float(dfT.iloc[-1,2]))

    diffLong = math.radians(np.float(dfT.iloc[-1,3]) - np.float(dfT.iloc[0,3]))

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    compass_bearing = np.float(compass_bearing)

    return compass_bearing

def tfile_Qest(tr_df):
    """
    Takes information from modified t_reader dataframe and generates cross-sectional velocity (V_cs),
    the water direction in relation to global coordinates (TWD_list), and the estimated discharge rates
    of each depth cell recorded by the ADP (Q)

    PLEASE NOTE: This function relies on the user setting the ADP for an XYZ coordinate system

    INPUTS
    - t_reader dataframe

    OUTPUTS
    - Initial r_reader dataframe with 3 additional columns:
        - V_cs: The cross sectional velocity perpendicular to the straight line between point A and point B of the transect
        - TWD: The converted water direction from XYZ (relative to ADP direction) plane to ENU (East-North-Upwards) plane
        - Q_est: The discharge perpendicular to the straight line of the transect from point A to point bug

    CONSIDERATIONS
    - The straight line between the first and last point of the transect may not be an accurate estimate of the true path conducted on the boat
    - Use Qnorm function below for most accurate measurement of discharge relative to boat path
    - The true water direction (TWD) relies on the ADP using an XYZ coordinate system, or the water direction relative to it's own orientation
        EX: If the ADP is facing East at 60 degrees, and the water direction it reads is 180 degrees, this means the true water direction relative
        to ENU coordinates is 240 degrees
    """
    bearing = T_transect_bearing(tr_df)
    TWD_list = []
    V_cs = []
    Q = []
    for x in range(0,len(tr_df)):
        if (tr_df.iloc[x,8] + tr_df.iloc[x,9] <= 360):
            TWD_list.append(tr_df.iloc[x,8] + tr_df.iloc[x,9])
        else:
            TWD_list.append((tr_df.iloc[x,8] + tr_df.iloc[x,9]) - 360)
    for i in range(0,len(TWD_list)):
        TWD = TWD_list[i]
        V = tr_df.iloc[i,7]
        V_cs.append(math.sin(math.radians(bearing - TWD)) *  V)

    for y in range(0,len(tr_df)):
        Q.append(tr_df.iloc[y,4] * (tr_df.iloc[1,6]-tr_df.iloc[0,6]) * V_cs[y])

    tr_df.insert(10, 'V_cs', V_cs)
    tr_df.insert(10, 'TWD', TWD_list)
    tr_df.insert(15, 'Q_est', Q)
    return tr_df

#=============================================== DIS file functions =====================================================================================================
def dis_reader(filename):
    """
    Takes cleaned up .dis file csv and repackages with date_time column and all
    profiles with data quality index (DQI) > 4 removed

    INPUTS
    - Cleaned up .dis file as csv (find example template in project appendix or in github)

    OUTPUTS
    - Filter .dis file as a readable dataframe
    """
    dis_df = pd.read_csv(str(filename), delimiter=',', skiprows=[3], header=4, skipfooter = 15, parse_dates=[1,2])
    dis_df= dis_df[dis_df['DQI'] < 4]
    return dis_df

def dis_transect_bearing(disfile):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """

    lat1 = math.radians(disfile.iloc[0,7])
    lat2 = math.radians(disfile.iloc[-1,7])

    diffLong = math.radians(disfile.iloc[-1,8] - disfile.iloc[0,8])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def dis_filter(filename):
"""
Takes dis_reader dataframe AS A CSV and returns useful information
"""

    df = pd.read_csv(str(filename), delimiter=',', skiprows=[3], header=4, skipfooter = 15)
    df= df[df['DQI'] < 4]
    date = df.iloc[0,1]
    time = df.iloc[0,2]
    bearing = dis_transect_bearing(df)
    max_depth= np.max(df['AvDepth(m)'])
    vel_avg = np.mean(df['uFlow(m/s)'])
    dir_avg = np.mean(df['DirFlow(deg)'])
    q_sum = np.sum(df['Q(m^3/s)'])
    total_area = df.iloc[0,4] * df.iloc[0,12]
    for x in range(1,len(df)):
        area = (df.iloc[x,4]-df.iloc[x-1,4]) * df.iloc[x,12]
        total_area = total_area+area
    return date, time, bearing, max_depth, vel_avg, dir_avg, q_sum, total_area

#=============================================== post analysis functions =====================================================================================================

def Qnorm(tr_df, dis_df, dt):
    """
    Merges t_reader and dis_reader dataframes to generate a master dataframe with all necessary information for assessing cross-sectional
    discharge

    INPUTS
    - tr_df: t_reader dataframe, a .T file which has undergone modifications from t_reader and tfile_Qest functions
    - dis_df: dis_reader dataframe
    - dt: the sampling interval used while sampling

    OUTPUTS
    - A master dataframe that includes all velocity, discharge, and orientation data for each individual depth-cell over each profile of the transect
    - Vn: The normalized velocity of the water relative to orientation and velocity of the boat and ADP
    - Qn: The normalized discharge rate of each depth cell relative to orientation and velocity of the boat and ADP
    """
    dis_df_sub = dis_df[['Profile', 'uVess(m/s)', 'DirVess(deg)']]
    df_merge = pd.merge(tr_df, dis_df_sub, how='inner', on="Profile")
    Qn = []
    Vn = []
    TVD = []
    dt = dt
    dz = df_merge.iloc[1,6] - df_merge.iloc[0,6]

    for x in range(0,len(df_merge)):
        if (df_merge.iloc[x,8] + df_merge.iloc[x,9] <= 360):
            TVD.append(df_merge.iloc[x,8] + df_merge.iloc[x,18])
        else:
            TVD.append((df_merge.iloc[x,8] + df_merge.iloc[x,18]) - 360)

    for y in range(0,len(df_merge)):
        theta = TVD[y]-df_merge.iloc[y,10]
        Qn.append((df_merge.iloc[y,7] * df_merge.iloc[y,17] * math.sin(math.radians(theta)) *  dt * dz))

    for i in range(0,len(df_merge)):
        phi = TVD[i]-df_merge.iloc[i, 10] + 90
        Vn.append((df_merge.iloc[i,7] * math.cos(math.radians(phi))))

    df_merge.insert(19, 'Qn', Qn)
    df_merge.insert(19, 'Vn', Vn)

    return df_merge

def dp_conversion(dfQ):
    """
    Converts master dataframe from Qnorm function into an xarray dataset, which is more easily accessible for depth-profile visualization

    INPUTS
    - Master dataframe from Qnorm function (df_merge)

    OUTPUTS
    - xarray dataset with cross-sectional and normalized velocities and discharge rates, organized by profile number and depth bin
    """
    unique_depth = np.unique(dfQ['Bin_depth'])
    unique_profile = np.unique(dfQ['Profile'])
    pivoted_V = dfQ.pivot(index='Profile',columns='Bin_depth',values='V')
    pivoted_Vcs = dfQ.pivot(index='Profile',columns='Bin_depth',values='V_cs')
    pivoted_Qest = dfQ.pivot(index='Profile',columns='Bin_depth',values='Q_est')
    pivoted_Vn = dfQ.pivot(index='Profile',columns='Bin_depth',values='Vn')
    pivoted_Qn = dfQ.pivot(index='Profile',columns='Bin_depth',values='Qn')
    dsQ = xr.Dataset({'V': (('profile', 'depth'), pivoted_V),'V_cs': (('profile', 'depth'), pivoted_Vcs), 'Q_est': (('profile', 'depth'), pivoted_Qest),
                     'Vn': (('profile', 'depth'), pivoted_Vn), 'Qn': (('profile', 'depth'), pivoted_Qn)},
                       {'profile': unique_profile, 'depth':unique_depth})
    return dsQ
