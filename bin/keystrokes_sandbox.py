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
    return parser.parse_args()
class KeyLog(object):
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
        with open(self.log_file, 'a') as f:
            f.write('%s,%2f\n'%(event.name, tdelta.total_seconds()))
            # f.write('{}\n'.format(event.name))
    def run(self,filein):
        vlc = '/c/Program\ Files/VideoLAN/VLC/vlc.exe'
        # code.interact(local=locals())
        # subprocess.Popen([vlc])
        subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",filein])
        # subprocess.call('vlc.exe %s'%(filein))
        # subprocess.call([vlc,filein])
        # os.system("%s %s"%(vlc,filein))
        keyboard.on_press(self.on_key_press)
        keyboard.wait('esc')
if __name__ == '__main__':
    args = parse_cmdline()
    Keys = KeyLog().run(args.mp4)
    # code.interact(local=locals())