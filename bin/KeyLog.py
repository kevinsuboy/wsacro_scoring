#!/usr/bin/env python

import argparse
from threading import Thread, Event
from pynput.keyboard import Key, Listener
import code
import subprocess
import os, sys
from datetime import datetime as dt
from datetime import timedelta as td
import time

def parse_cmdline():
    parser = argparse.ArgumentParser(
        prog='keystrokes.py',
        description='',
        epilog=''
    )
    parser.add_argument('-v', '--mp4',action="store",help='',required=True) 
    parser.add_argument('-o', '--output',action="store",help='',required=True) 
    return parser.parse_args()

class KeyLog(object):
    def __init__(self,log_file='keystrokes.txt'):
        os.system("rm -rf %s"%(log_file))
        self.log_file = log_file
        self.log = []
        self.start = None

    def on_press(self,key):
        # print('{0} pressed'.format(
            # key))
        if not self.start:
            self.start = dt.now()
        tdelta = dt.now()-self.start
        self.log.append([tdelta,key])
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write('%s,%2f\n'%(key, tdelta.total_seconds()))

    def on_release(self,key):
        # print('{0} release'.format(
            # key))
        if key == Key.esc:
            # Stop listener
            return False
    def run(self,filein):
        # vlc = '/c/Program\ Files/VideoLAN/VLC/vlc.exe'
        subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",filein])
        with open(self.log_file, 'a') as f:
            f.write('key,time_delta\n')
        with Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()
        return self.log

if __name__ == "__main__":
    args = parse_cmdline()
    # Collect events until released
    Keys = KeyLog(args.output).run(args.mp4)