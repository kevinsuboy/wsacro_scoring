#!/usr/bin/env python
from threading import Thread
import cv2, time
import code
from datetime import datetime as dt
from datetime import timedelta as td
def decode_fourcc(cc):

    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
class ThreadedVideo(object):
    def __init__(self, src=0, comp_start=td(seconds=200),comp_time=td(seconds=157),mode=None,fout="__final__"):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
       
        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/self.capture.get(cv2.CAP_PROP_FPS)
        # breakpoint()
        self.FPS_MS = int(self.FPS * 1000)
        
        self.done = False
        self.start = False
        self.comp_start = comp_start
        self.time = comp_time
        self.elapsed = 0
        self.mode = mode
        # self.timer = 0
        # self.timer = False
        # self.start = False
        # code.interact(local=locals())
        # Start frame retrieval thread
        print(decode_fourcc(self.capture.get(cv2.CAP_PROP_FOURCC)))
        # print(decode_fourcc(cv2.VideoWriter_fourcc(*'h264')))
        self.fout = cv2.VideoWriter(
                        # '%s.mp4'%(fout),  
                        '%s.mkv'%(fout),  
                        # cv2.VideoWriter_fourcc(*'avc1'), 
                        # cv2.VideoWriter_fourcc(*'h264'), 
                        cv2.VideoWriter_fourcc(*'FMP4'), 
                        # cv2.VideoWriter_fourcc(*'mp4v'), 
                        self.capture.get(cv2.CAP_PROP_FPS), (int(self.capture.get(3)),int(self.capture.get(4))),
                        True) 
        # code.interact(local=locals())
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        ##
        
    def update(self):
        while not self.done:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
                self.cfn = self.capture.get(1)
                self.t_cur = td(seconds = round(self.cfn*self.FPS,2))
                self.mod_frame()
                # code.interact(local=locals())
                if not self.status:
                    self.done = True
                # breakpoint()
                # if self.status:
                #     self.timer += self.FPS
                # if not self.start:
                #     self.start = time.time()
                # self.timer = time.time()-self.start
            # time.sleep(self.FPS)
    def mod_frame(self):
        font = cv2.FONT_HERSHEY_DUPLEX 
        # print(t_cur)
        # print(self.comp_start)
        # print(t_cur >= self.comp_start)
        print_time = self.time
        if(self.t_cur >= self.comp_start):
            self.elapsed = self.t_cur - self.comp_start
            print_time = self.time - self.elapsed
            # code.interact(local=locals())
        cv2.putText(self.frame, str(print_time.total_seconds()),  
                (200, 250), font, 
                5, (0, 255, 255), 
                10, cv2.LINE_AA)
        if self.mode != "start":
            self.fout.write(self.frame)
        # else:
    def show_frame(self):
        if self.status:
            if self.mode == "start":
                cv2.imshow('frame', self.frame)
            key = cv2.waitKey(round(self.FPS_MS/10))
            if self.mode == "start":
                if key == ord('k') and not self.start:
                    self.done = True
                    self.comp_start = self.t_cur
                return
            if key == ord('q'):
                self.done = True
                return

    def join(self):
        self.done = True
        self.thread.join()
        self.fout.release()
        self.capture.release()
        cv2.destroyAllWindows()
        return self.comp_start

if __name__ == '__main__':
    src = '../../output2.MP4'
    # src = 'https://videos3.earthcam.com/fecnetwork/9974.flv/chunklist_w1421640637.m3u8'
    threaded_camera = ThreadedVideo(src)
    while not threaded_camera.done:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass
    threaded_camera.join()
    