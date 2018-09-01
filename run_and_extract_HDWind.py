#!/usr/bin/env python
"""
CSV data to windini_N.asc
"""
import os
import shutil
import pandas as pd
import argparse

HDWM_OPT = os.environ['HDWM_OPT']
HDWM_OPT_DATA = os.environ['HDWM_OPT_DATA']
HDWM_OPT_RESULTS = os.environ['HDWM_OPT_RESULTS']

def run(path_datos, path_results):
    """dataframe in csv format, datum WGS84, epsg:4326:
        header: date,lat,lon,name,wind_dir,wind_speed
    """
    data = pd.read_csv(path_datos, parse_dates=['date'])
    name_path_datos, extension_file = path_datos.split("/").pop().split(".")
    data = data.sort_values('date')
    N = data.groupby('date')

    for name, group in N:
        with open('windini_0.asc', 'w') as f:
            f.write('ReferenceSystem 1' + '\n')
            f.write('InputPoints ' + str(len(group)) + '\n')
            for index, input_data in group.iterrows():
                f.write(
                    str(input_data.lat) + ' ' + str(input_data.lon) + ' ' +
                    str('10') + ' ' + str(input_data.wind_speed) +
                    ' ' + str(input_data.wind_dir) + '\n')

            f.write('OutputLayers 20' + '\n' + '10  20  30 40 50 60 80 90 100 150 200 250 300 350 400 450 500 600 800 900' + '\n')
            f.write('OutputPoints 0' + '\n')
        os.remove(HDWM_OPT_DATA + '/windini_0.asc')
        shutil.move('windini_0.asc', HDWM_OPT_DATA)
        os.system(HDWM_OPT + "/build/HDWM")
        shutil.move(HDWM_OPT_RESULTS +'/coronelWind.dat', path_results+'/'+str(name)+'.dat')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='data-HDWind-data', description='input data to HDWind model and output data')
    parser.add_argument('-d', default=os.getcwd(),
                        help='dir to input data csv ')
    parser.add_argument('-r', help='path to put the results')
    args = parser.parse_args()
    run(args.d, args.r)
