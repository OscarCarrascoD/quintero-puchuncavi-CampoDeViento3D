""" 
Leer csvs_path, 
consolidar DataFrame: date,lat,lon,wind_dir,wind_speed,name
exportar DataFrame
"""

import pandas as pd
import datetime as dt
import glob
import os
import re
import pyproj

inProj = pyproj.Proj(init='epsg:5361')
outProj = pyproj.Proj(init='epsg:4326')
data_format = lambda fecha,hora: pd.to_datetime(fecha+hora, format='%y%m%d%H%M')

def get_name_station(csvs_file):
    return os.path.basename(csvs_file).replace('.csv','').split('-').pop()

def locationUTM_to_WGS84_station(csvs_file):
    p = re.compile(r'\d+')
    N, E = p.findall(os.path.basename(csvs_file).strip('.csv').split('-')[2])
    lon,lat = pyproj.transform(inProj,outProj,N,E)
    return f'{float(lat):.6f}', f'{float(lon):.6f}'

csvs_path = './csv-quintero'
csvs_files = sorted(glob.glob(csvs_path + '/*.csv'))
quinteros_DataFrame = pd.DataFrame()
stations_DataFrame = [['name','lat','lon']]
stations = set([ get_name_station(csvs_file) for csvs_file in csvs_files ] )
for station in stations:
    list_of_True = [('-'+station+'.') in csvs_file for csvs_file in csvs_files]
    index_station = [i for i,val in enumerate(list_of_True) if val==True]
    if ('-VEL-') in csvs_files[index_station[0]]:
        vel_path = csvs_files[index_station[0]]
        dir_path = csvs_files[index_station[1]]
    else:
        dir_path = csvs_files[index_station[0]]
        vel_path = csvs_files[index_station[1]]
    vel_df = pd.read_csv(vel_path, header=None, delimiter=';', decimal=',', skiprows=1,usecols=[0, 1, 2], names=['fecha','hora','wind_speed'], parse_dates = {'date': [0, 1]},date_parser=data_format)
    dir_df = pd.read_csv(dir_path, header=None, delimiter=';', decimal=',', skiprows=1,usecols=[0, 1, 2], names=['fecha','hora','wind_dir'], parse_dates = {'date': [0, 1]},date_parser=data_format)
    lat,lon = locationUTM_to_WGS84_station(vel_path)
    stations_DataFrame.append([station,lat,lon])
    df = pd.merge(vel_df, dir_df, how='inner', on='date')
    df['name'],df['lat'],df['lon'] = station,lat,lon
    df.dropna(inplace=True)
    quinteros_DataFrame = quinteros_DataFrame.append(df)
    pass
quinteros_DataFrame.to_csv("quinteros.csv", index=False)
pd.DataFrame(stations_DataFrame[1:], columns=stations_DataFrame[0]).to_csv('stations.csv', index=False)
