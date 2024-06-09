#!/usr/bin/env python
import argparse
import code
import os, subprocess
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta as td
import pandas as pd
import numpy as np

def parse_cmdline():
    parser = argparse.ArgumentParser(
        prog='parse_flysight.py',
        description='',
        epilog=''
    )
    parser.add_argument('-f', '--filein',action="store",help='') 
    parser.add_argument('-fly', '--flysight',action="store",type=int,help='') 
    return parser.parse_args()
def get_flysight(filein):
    df = pd.read_csv(filein,parse_dates=['time'])
    t_start = df[(df["velD"]>=9) & (df["hMSL"] > 3000)].iloc[0]['time'] - td(seconds=1)
    df_start = df[(df["time"] >= t_start)].iloc[0]
    comp_run = df[(df["time"] >= df_start["time"]) & (df["hMSL"] >= df_start["hMSL"] - 2286)]
    # df['accel_D'] = (df['velD'] - df['velD'].shift(1)) / (df['time'] - df['time'].shift(1)).dt.total_seconds()
    plot_run = df[(df["time"] >= df_start["time"]-td(seconds=10)) & (df["hMSL"] >= 500)]
    return plot_run, comp_run, comp_run.iloc[-1]["time"] - comp_run.iloc[0]["time"]
def convert_flysight(filein,fly = None):
    # code.interact(local=locals()) 
    if fly == 3:
        fN = "f3"
        rm_lines = "1d;2d;3d;4d;6d;7d;"
    else:
        fN = "f2"
        rm_lines = '2d;'
    if fly:
        new_file = "%s_%s.%s"%(filein.split('.')[0],fN,filein.split('.')[-1])
        os.system("sed '%s' %s > %s"%(rm_lines, filein, new_file))
        os.system("sed -i 's/$COL,//g' %s"%(new_file))
        return new_file
    return filein

if __name__ == '__main__':
    args = parse_cmdline()
    filein = convert_flysight(args.filein,args.flysight)
    # code.interact(local=locals())
    plot_run, comp_run, comp_time = get_flysight(filein)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax3 = ax2.twinx()
    plot_run.plot(ax=ax1,x='time',y=['hMSL'])
    plot_run.plot(ax=ax2,x='time',y=['velD'])
    plt.title("COMP TIME IS %d.%ds"%(comp_time.seconds,comp_time.microseconds))
    # comp_run.plot(ax=ax3,x='time',y=['accel_D'],ylim=[0,15])
    plt.show()
    # code.interact(local=locals())
