#!/usr/bin/env python
import argparse
import ThreadedVideo as tv
import parse_flysight as pf
import os
import code
from datetime import datetime as dt
from datetime import timedelta as td

def parse_cmdline():
    parser = argparse.ArgumentParser(
        prog='convert.py',
        description='',
        epilog=''
    )
    parser.add_argument('-s', '--slate',action="store",help='slate start',required=True) 
    parser.add_argument('-c', '--comp',action="store",help='comp start, from plane exit',required=True) 
    parser.add_argument('-f', '--flysight',action="store",help='',required=True) 
    parser.add_argument('-v', '--mp4',action="store",help='',required=True) 
    parser.add_argument('-o', '--output',action="store",help='',required=True) 
    return parser.parse_args()
if __name__ == '__main__':
    args = parse_cmdline()
    plot_run, comp_run, comp_time = pf.get_flysight(args.flysight)
    slate_beg = dt.strptime(args.slate,"%H:%M:%S") - td(seconds=5)
    slate_end = dt.strptime(args.slate,"%H:%M:%S") + td(seconds=5)
    comp_beg = dt.strptime(args.comp,"%H:%M:%S") - td(seconds=5)
    # comp_end = dt.strptime(args.comp,"%H:%M:%S")
    comp_end = dt.strptime(args.comp,"%H:%M:%S") + comp_time

    os.system("rm -rf __tmp__.mp4")
    os.system("ffmpeg -ss %s -to %s -i %s -vcodec copy -acodec copy __tmp__.mp4"%(dt.strftime(comp_beg,"%H:%M:%S"),dt.strftime(comp_end,"%H:%M:%S"),args.mp4))
    # os.system("ffmpeg -ss %s -to %s -i %s -vcodec copy -acodec copy %s_slate.mp4"%(dt.strftime(slate_beg,"%H:%M:%S"),dt.strftime(slate_end,"%H:%M:%S"),args.mp4,args.output))
    # code.interact(local=locals()) 
    # quit()
    comp_start = 0
    samples = 1
    for i in range(samples):
        threaded_camera = tv.ThreadedVideo('./__tmp__.mp4', comp_time=comp_time, mode="start")
        while not threaded_camera.done:
            try:
                threaded_camera.show_frame()
            except AttributeError:
                pass
        comp_start += threaded_camera.join().total_seconds()
    comp_start /= samples

    comp_end = comp_beg + td(seconds=comp_start) + comp_time
    # code.interact(local=locals()) 
    # os.system("rm -rf __tmp__.mp4")
    # os.system("ffmpeg -ss %s -to %s -i %s -vcodec copy -acodec copy __tmp__.mp4"%(dt.strftime(comp_beg,"%H:%M:%S"),dt.strftime(comp_end,"%H:%M:%S"),args.mp4))

    threaded_camera = tv.ThreadedVideo('./__tmp__.mp4', comp_start=td(seconds=comp_start), comp_time=comp_time)
    while not threaded_camera.done:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass
    
    