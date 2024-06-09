#!/usr/bin/env python

import argparse
import keyboard
import code
import subprocess
import os, sys
from datetime import datetime as dt
from datetime import timedelta as td

def parse_cmdline():
    parser = argparse.ArgumentParser(
        prog='keystrokes.py',
        description='',
        epilog=''
    )
    parser.add_argument('-v', '--mp4',action="store",help='',required=True) 
    parser.add_argument('-o', '--output',action="store",help='',required=True) 
    return parser.parse_args()
class KeyLog_old(object):
    def __init__(self,log_file='keystrokes.txt'):
        os.system("rm -rf %s"%(log_file))
        self.log_file = log_file
        self.log = []
        self.start = None
    def on_key_press(self,event):
        if not self.start:
            self.start = dt.now()
        tdelta = dt.now()-self.start
        self.log.append([tdelta,event.name])
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write('%s,%2f\n'%(event.name, tdelta.total_seconds()))
    def run(self,filein):
        # vlc = '/c/Program\ Files/VideoLAN/VLC/vlc.exe'
        subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",filein])
        keyboard.on_press(self.on_key_press)
        keyboard.wait('esc')
        return self.log
if __name__ == '__main__':
    args = parse_cmdline()
    Keys = KeyLog_old(args.output).run(args.mp4)
    print(Keys)
    # code.interact(local=locals())