#!/usr/bin/env python

import os
import glob
import datetime
import argparse
import pandas as pd
import numpy as np
import math
import colorlover as cl
import plotly.graph_objs as go
from plotly.offline import plot

def wind_bft(wind_speed):
    """Convert wind from metres per second to Beaufort scale"""
    BEAUFORT_SCALE_MS = np.array(
        '0.3 1.5 3.4 5.4 7.9 10.7 13.8 17.1 20.7 24.4 28.4 32.6'.split(),
        dtype='float64')
    BEAUFORT_SCALE_DESCRIPTION = np.array(['Calma', 'Ventolina', 'Flojito', 'Flojo', 'Bonancible', 'Fresquito', 'Fresco', 'Frescachón', 'Temporal', 'Temporal fuerte', 'Temporal duro', 'Temporal muy duro', 'Temporal huracanado'])
    if wind_speed is None:
        return None
    else:
        return BEAUFORT_SCALE_DESCRIPTION[np.digitize(wind_speed, BEAUFORT_SCALE_MS)]

def wind_cat(wind_dir):
    """Convert wind from metres per second to Cardinal direction"""
    DIRECTIONS_CATEGORICAL = np.array(
        'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW N'.split())
    DIRECTIONS_NUMERICAL = np.arange(11.25, 372, 22.5)
    if wind_dir is None:
        return None
    else:
        return DIRECTIONS_CATEGORICAL[np.digitize(wind_dir, DIRECTIONS_NUMERICAL)]

def wind_rose_plot(df_wind_rose):
    data = []
    wind_rose = pd.DataFrame({'wind_dir_cat': np.array('N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW'.split()), 'wind_dir': [0]*16})
    i = 0
    bfs = df_wind_rose.groupby('wind_speed_bfs')
    color = cl.scales[str(df_wind_rose.wind_speed_bfs.unique().shape[0]+1)]['qual']['Set1']
    for bfs_wind, group_bfs in bfs:
        df1 = pd.DataFrame({'wind_dir_cat': group_bfs.wind_dir_cat.value_counts().index, 'wind_dir': group_bfs.wind_dir_cat.value_counts().values})
        df2 = pd.merge(wind_rose, df1, how='left', on='wind_dir_cat').fillna(0)
        data.append(go.Area(t=df2.wind_dir_cat, r=df2.wind_dir_y.fillna(0), marker=dict(color=color[i]), name=bfs_wind))
        i += 1
    layout_windrose = dict(title='Rosa de los vientos de ' + df_wind_rose.model_name.iloc[0].title() + 'en ' + df_wind_rose.name.iloc[0].title(), orientation=270, barmode='stack',)
    plot(dict(data=data, layout=layout_windrose), filename=df_wind_rose.model_name.iloc[0].title()+ '_'+ df_wind_rose.name.iloc[0].title() + 'windrose.html', auto_open=False, image='png', image_filename=df_wind_rose.model_name.iloc[0].title()+ '_'+ df_wind_rose.name.iloc[0].title())


def wind(path_data, path_plot):

    wind_dataFrame = pd.read_csv(path_data, parse_dates=['date'])
    wind_dataFrame['model_name'] = wind_dataFrame['name']

    wind_dataFrame['wind_dir_cat'] = wind_cat(wind_dataFrame.wind_dir)
    wind_dataFrame['wind_speed_bfs'] = wind_bft(wind_dataFrame.wind_speed)
    N = wind_dataFrame.groupby('name')

    os.chdir(path_plot)

    color = cl.scales[str(len(N)+1)]['qual']['Set1']
    for name, group in N:
        i = 0
        trace_speed = []
        trace_dir = []
        df_wind_rose_1 = group[group.name == name]
        wind_rose_plot(df_wind_rose_1[['wind_speed_bfs', 'wind_dir_cat', 'model_name', 'name']])
        date = group[group.name == name].date
        speed = group[group.name == name].wind_speed
        direc = group[group.name == name].wind_dir
        trace_speed.append(go.Scatter(x=date, y=speed, mode='lines+markers', name='Observado', line=dict(color=color[i])))
        trace_dir.append(go.Scatter(x=date, y=direc, mode='lines+markers', name='Observado', line=dict(color=color[i])))
        i += 1
        layout_speed = dict(title='Velocidad en el tiempo ' + name.title(),
                            xaxis=dict(title='Tiempo'), yaxis=dict(title='V [m/s]'), plot_bgcolor='rgb(229,229,229)',)
        plot(dict(data=trace_speed, layout=layout_speed), filename=name +
             'speed.html', auto_open=False, image='png', image_filename=name)
        layout_dir = dict(title='Dirección en el tiempo ' + name.title(),
                          xaxis=dict(title='Tiempo'), yaxis=dict(title='Grados '), plot_bgcolor='rgb(229,229,229)',)
        plot(dict(data=trace_dir, layout=layout_dir), filename=name +
             'direction.html', auto_open=False, image='png', image_filename=name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='csv to wind plots', description='plot data')
    parser.add_argument('-d', help='path to csv with observed data')
    parser.add_argument('-p', help='path to place plots', default=os.getcwd())
    parser.add_argument
    args = parser.parse_args()
    wind(args.d, args.p)