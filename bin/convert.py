#!/usr/bin/env python
import argparse
import ThreadedVideo as tv
import parse_flysight as pf
import os
import code
from datetime import datetime as dt
from datetime import timedelta as td

def parse_cmdline(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(
            prog='convert.py',
            description='',
            epilog=''
        )
    parser.add_argument('-s', '--slate',action="store",help='slate start',required=True) 
    parser.add_argument('-c', '--comp',action="store",help='comp start, from plane exit',required=True) 
    parser.add_argument('-f', '--flysight',action="store",help='',required=True) 
    parser.add_argument('-fly', '--fver',action="store",help='',required=True) 
    parser.add_argument('-v', '--mp4',action="store",help='',required=True) 
    parser.add_argument('-o', '--output',action="store",help='',required=True) 
    parser.add_argument('-nr', '--no_redo',action="store_true",help='') 
    return parser.parse_args()
class Convert(object):
    def __init__(self,flysight,fver,slate,comp,output,mp4):
        self.DEFAULT_COMP_PAD = 5
        self.DEFAULT_SLATE_PAD = 5
        self.DEFAULT_SAMPLES = 1
        self.DEFAULT_COMP_TIME = 60
        tmp = output.split('/')
        self.fout_dir = '/'.join(tmp[0:-1])
        self.fout = tmp[-1]
        self.mp4 = mp4
        if flysight:
            self.plot_run, self.comp_run, self.comp_time = pf.get_flysight(pf.convert_flysight(flysight,fver))
        else:
            self.comp_time = td(seconds=self.DEFAULT_COMP_TIME)
        slate = dt.strptime(slate,"%H:%M:%S")
        comp = dt.strptime(comp,"%H:%M:%S")
        zero = (slate - dt.strptime("00:00:00","%H:%M:%S")) >= td(seconds=self.DEFAULT_SLATE_PAD)
        # code.interact(local=locals())
        self.slate_beg = (slate - td(seconds=self.DEFAULT_SLATE_PAD)) if zero else slate
        self.slate_end = slate + td(seconds=self.DEFAULT_SLATE_PAD)
        zero = (comp - dt.strptime("00:00:00","%H:%M:%S")) >= td(seconds=self.DEFAULT_COMP_PAD)
        self.comp_beg = (comp - td(seconds=self.DEFAULT_COMP_PAD)) if zero else comp
        # comp_end = comp
        self.comp_end = comp + self.comp_time + td(seconds=self.DEFAULT_COMP_PAD)
    def convert_format(self):
        os.system("rm -rf %s/__%s_tmp__.mp4"%(self.fout_dir,self.fout))
        os.system("rm -rf %s/slate_%s.mp4"%(self.fout_dir,self.fout))
        os.system("ffmpeg -ss %s -to %s -i %s -vf scale=1280:720 -r 30 -an %s/__%s_tmp__.mp4"%(dt.strftime(self.comp_beg,"%H:%M:%S"),dt.strftime(self.comp_end,"%H:%M:%S"),self.mp4,self.fout_dir,self.fout))
        # os.system("ffmpeg -ss %s -to %s -i %s -vcodec copy -acodec copy %s/__%s_tmp__.mp4"%(dt.strftime(self.comp_beg,"%H:%M:%S"),dt.strftime(self.comp_end,"%H:%M:%S"),self.mp4,self.fout_dir,self.fout))
        os.system("ffmpeg -ss %s -to %s -i %s -vf scale=1920:1080 -r 30 -an %s/slate_%s.mp4"%(dt.strftime(self.slate_beg,"%H:%M:%S"),dt.strftime(self.slate_end,"%H:%M:%S"),self.mp4,self.fout_dir,self.fout))
        # os.system("ffmpeg -ss %s -to %s -i %s -vcodec copy -acodec copy %s/slate_%s.mp4"%(dt.strftime(self.slate_beg,"%H:%M:%S"),dt.strftime(self.slate_end,"%H:%M:%S"),self.mp4,self.fout_dir,self.fout))

        # code.interact(local=locals()) 
        # quit()
    def get_start(self):
        # input("Press Enter to continue...")
        self.comp_start = 0
        for i in range(self.DEFAULT_SAMPLES):
            threaded_camera = tv.ThreadedVideo('%s/__%s_tmp__.mp4'%(self.fout_dir,self.fout), comp_time=self.comp_time, mode="start")
            while not threaded_camera.done:
                try:
                    threaded_camera.show_frame()
                except AttributeError:
                    pass
            self.comp_start += threaded_camera.join().total_seconds()
        self.comp_start /= self.DEFAULT_SAMPLES
    def save_video(self,scores,rtype,dock_list,freelist):
        threaded_camera = tv.ThreadedVideo('%s/__%s_tmp__.mp4'%(self.fout_dir,self.fout), comp_start=td(seconds=self.comp_start), comp_time=self.comp_time, fout=self.fout_dir+"/"+self.fout, scores=scores, dock_list=dock_list, freelist=freelist, mode=rtype)
        while not threaded_camera.done:
            try:
                threaded_camera.show_frame()
            except AttributeError:
                pass
if __name__ == '__main__':
    args = parse_cmdline()
    conv = Convert(args.flysight,args.fver,args.slate,args.comp,args.output,args.mp4)
    if not args.no_redo:
        conv.convert_format()
    conv.get_start()
    # conv.save_video()


    
    