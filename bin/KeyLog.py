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
        formatter_class=argparse.RawTextHelpFormatter,
        description=
        "---Score logger--- \n" \
        "<space>: sync to exit \n" \
        "• +: Point complete \n" \
        "Incomplete points \n\n" \
        "• -: Bad Grip \n" \
        "• 0: Camera View \n" \
        "• *: No Attempt \n\n" \
        "<esc> for next video \n\n\n" \
        "======== Style Guide ========\n" \
        "• 9-10 points - Routine is performed flawlessly with no noticeable mistakes.\n" \
        "• 6-9 points - Routine is performed with small mistake(s).\n" \
        "• 3-7 points - Routine is performed with medium mistake(s).\n" \
        "• 1-4 points - Routine is performed with large mistake(s).\n" \
        "• 0-1 points - Routine is not performed or not identifiable.\n"\
        "\n======== Camera Guide ========\n" \
        "3.1. Quality\n" \
        "• 6-7 points - Camerawork is performed flawlessly with no noticeable mistakes.\n" \
        "• 4-6 points - Camerawork is performed with small mistake(s).\n" \
        "• 2-5 points - Camerawork is performed with medium mistake(s).\n" \
        "• 1-3 points - Camerawork is performed with large mistake(s).\n" \
        "• 0-1 points - Camerawork is shows no Performer maneuvers.\n" \
        "3.2. Progressive Work\n" \
        "• 3 points - Routine is performed with a significant amount of successful progressive work.\n" \
        "• 2 points - Routine is performed with some successful progressive work.\n" \
        "• 1 point - Routine is performed with minimal progressive work.\n" \
        "• 0 points - Routine is performed with no progressive work.\n" \
        "\n======== Dive Plan Guide ========\n" \
        "4.1. Technical\n" \
        "• Variety of moves: Performs several types of moves (using different orientations) within the Dive Plan\n" \
        "• Difficulty: The degree of difficulty of all moves and transitions in the routine\n" \
        "• Teamwork: The amount and type of teamwork within the dive plan – constant interaction, showing combined skills of all Team\n" \
        "Members, synchronization with the cameraman\n" \
        "• Working time management: Ability to utilize working time and work the dive plan into the time allotted.\n" \
        "• Grip complexity, if present\n",
        epilog=''
    )
    parser.add_argument('-v', '--mp4',action="store",help='',required=True) 
    parser.add_argument('-o', '--output',action="store",help='',required=True) 
    return parser.parse_args()

class KeyLog(object):
    def __init__(self,log_file='keystrokes.txt',round="C"):
        os.system("rm -rf %s"%(log_file))
        self.log_file = log_file
        self.log = []
        self.start = None
        self.round = round
        self.accepted = ['+','-','0','*']

    def on_press(self,key):
        # print('{0} pressed'.format(
            # key))
        # code.interact(local=locals())
        if key != Key.esc and (key == Key.space or key.char in self.accepted):
            if not self.start:
                self.start = dt.now()
            tdelta = dt.now()-self.start
            self.log.append([tdelta,key])
            if self.log_file:
                with open(self.log_file, 'a') as f:
                    row = '%s,%2f,,'%(key, tdelta.total_seconds())
                    if self.round == "F":
                        row += ',,'
                    row += '\n'
                    f.write(row)

    def on_release(self,key):
        # print('{0} release'.format(
            # key))
        if self.round == 'F':
            return False
        if key == Key.esc:
            # Stop listener
            return False
    def run(self,filein):
        print("\n====== scoring for %s ======"%(filein))
        print("Press <esc> when done\n")
        # vlc = '/c/Program\ Files/VideoLAN/VLC/vlc.exe'
        subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",filein])
        with open(self.log_file, 'a') as f:
            header = 'key,time_delta,comments,style'
            if self.round == "F":
                header += ',dive_plan,camera_quality,camera_prog'
            header += '\n'
            f.write(header)
        with Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()
            final = ",,,"+input("Please enter style score: ")
            if self.round == "F":
                final += "," + input("Please enter dive_plan score: ")
                final += "," + input("Please enter camera_quality score: ")
                final += "," + input("Please enter camera_prog score: ")
            with open(self.log_file, 'a') as f:
                f.write('%s\n'%(final))
        return self.log

if __name__ == "__main__":
    args = parse_cmdline()
    # Collect events until released
    Keys = KeyLog(args.output).run(args.mp4)
    code.interact(local=locals())
