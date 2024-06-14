#!/usr/bin/env python
from threading import Thread
import cv2, time
import code
from datetime import datetime as dt
from datetime import timedelta as td
import pandas as pd
import argparse
def decode_fourcc(cc):

    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
def parse_cmdline(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(
            prog='score_round.py',
            description='',
            epilog=''
        )
    parser.add_argument('-src', '--source',action="store",help='',required=True) 
    return parser.parse_args()
class ThreadedVideo(object):
    def __init__(self, src=0, comp_start=td(seconds=200),comp_time=td(seconds=157),mode=None,fout="__final__",scores=None,dock_list=None,freelist=None,seq="n n n"):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
       
        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/self.capture.get(cv2.CAP_PROP_FPS)
        # breakpoint()
        self.FPS_MS = int(self.FPS * 1000)
        # code.interact(local=locals())
        self.WIDTH  = self.capture.get(3)   # float `width`
        self.HEIGHT = self.capture.get(4)  # float `height`
        self.FONT_SCALER = round(self.HEIGHT/780)

        self.done = False
        self.start = False
        self.comp_start = comp_start
        self.time = comp_time
        self.elapsed = None
        self.mode = mode
        self.seq = seq
        self.scores = scores
        self.incr_flag = False
        if isinstance(dock_list, pd.DataFrame):
            self.dstr = dock_list.to_string(index=False).split('\n')
            self.judges = dock_list.index
        self.strl = []
        if freelist:
            for i in range(len(freelist['style'])):
                self.strl.append("%.1f                 %.1f                 %.1f (%.1f + %.1f)"%(freelist['style'][i],freelist['dive_plan'][i],sum(freelist['camera'][i]),freelist['camera'][i][0],freelist['camera'][i][1]))
            self.judges = freelist['judges']
        self.pts = 0
        self.cont = True
        self.key_dict = {
            "'+'": "",
            "'-'": "Bad Grip",
            "'0'": "Camera View",
            "'*'": "No Attempt"
        }
        if scores:
            _,_,_,self.style,self.dive_plan,self.camera = self.scores.pop()
            self.dfinal_str = " ".join([el[0] for el in self.scores[1:]])
            # code.interact(local=locals())
            if self.mode == "C":
                self.scores.reverse()
                self.scores.pop() # first is a sync
                self.get_scores()
        # self.timer = 0
        # self.timer = False
        # self.start = False
        # code.interact(local=locals())
        # Start frame retrieval thread
        # print(decode_fourcc(self.capture.get(cv2.CAP_PROP_FOURCC)))
        # print(decode_fourcc(cv2.VideoWriter_fourcc(*'h264')))
        # tmp = fout.split('/')
        # fout = tmp[-1]
        # fout_dir = '/'.join(tmp[0:-1])
        # fout_dir = '.' if not fout_dir else fout_dir
        # code.interact(local=locals())
        if len(fout.split('/'))>1:
            self.rn,self.teamname = fout.split('/')[-2:]
            self.rn = self.rn.split('_')[0]
        else:
            self.rn,self.teamname = 0, "ghost"
        self.fout = cv2.VideoWriter(
                        # '%s.mp4'%(fout),  
                        '%s.mkv'%(fout),  
                        # '%s/_%s.mkv'%(fout_dir,fout),  
                        # cv2.VideoWriter_fourcc(*'avc1'), 
                        # cv2.VideoWriter_fourcc(*'h264'), 
                        cv2.VideoWriter_fourcc(*'FMP4'), 
                        # cv2.VideoWriter_fourcc(*'mp4v'), 
                        self.capture.get(cv2.CAP_PROP_FPS), (int(self.capture.get(3)),int(self.capture.get(4))),
                        True) 
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        ##
    def get_scores(self):
        if not self.scores:
            return False
        self.key, self.score,self.comments,_,_,_ = self.scores.pop()
        return True

    def update(self):
        while not self.done:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
                # code.interact(local=locals())
                self.cfn = self.capture.get(1)
                self.t_cur = td(seconds = round(self.cfn*self.FPS,2))
                self.mod_frame()
                if not self.status:
                    self.done = True
                # breakpoint()
                # if self.status:
                #     self.timer += self.FPS
                # if not self.start:
                #     self.start = time.time()
                # self.timer = time.time()-self.start
            if self.mode == "start":
                time.sleep(self.FPS*0.85)
    def draw_rect(self,pos,delta):
        x,y = [round(el) for el in pos]
        dx,dy = [round(el) for el in delta]
        cv2.rectangle(self.last_frame, (x-self.FONT_SCALER*10, y+self.FONT_SCALER*10), (x+dx, y+dy), (0,0,0), -1)
    def print_res(self,el0,ele,font):
        stX = round(.12*self.WIDTH)
        stY = round(.12*self.HEIGHT)
        dY = round(.064*self.HEIGHT)
        stX2 = round(.039*self.WIDTH)
        cv2.putText(self.last_frame, el0,
                (stX,stY), font, 
                self.FONT_SCALER*0.515, (255, 255, 255), 
                self.FONT_SCALER*1, cv2.LINE_AA)
        for i,line in enumerate(ele):
            cv2.putText(self.last_frame, self.judges[i],
                    (stX2, stY+dY*(i+1)), font, 
                    self.FONT_SCALER*0.5, (255, 255, 255), 
                    self.FONT_SCALER*1, cv2.LINE_AA)
            cv2.putText(self.last_frame, line.replace("'"," "),
                    (stX, stY+dY*(i+1)), font, 
                    self.FONT_SCALER*0.5, (255, 255, 255), 
                    self.FONT_SCALER*1, cv2.LINE_AA)
        cv2.putText(self.last_frame, self.dfinal_str.replace("'"," "),
                (stX, stY+dY*(len(ele)+1)), font, 
                self.FONT_SCALER*0.5, (255, 0, 255), 
                self.FONT_SCALER*1, cv2.LINE_AA)

    def mod_frame(self):
        font = cv2.FONT_HERSHEY_DUPLEX 
        # print(t_cur)
        # print(self.comp_start)
        # print(t_cur >= self.comp_start)
        print_time = self.time
        print_point = False
        print_final = False
        if(self.t_cur >= self.comp_start):
            self.elapsed = self.t_cur - self.comp_start
            print_time = self.time - self.elapsed
        if(self.mode == 'C' and self.cont and self.elapsed and self.elapsed >= td(seconds=0)):
            delt = (self.score - self.elapsed)
            if (print_time.total_seconds() >= 0.00): 
                if(delt.total_seconds() <= 0.0 and delt.total_seconds() >= -0.5):
                    print_point = True
                    if not self.incr_flag:
                        self.pts+=1 if self.key == "'+'" else 0
                        self.incr_flag = True
                elif delt.total_seconds() < 0:
                    self.incr_flag = False
                    # print(delt)
                    self.cont = self.get_scores()
                    # if self.pts == 25:
                    #     code.interact(local=locals ())

        if print_time >= td(seconds=0):
            self.last_frame = self.frame
        elif print_time <= td(seconds=-1):
            print_final = True
            print_time = td(seconds=0)
            self.cont = self.get_scores()
        else:
            print_time = td(seconds=0)
        pos = (round(.156*self.WIDTH), round(.064*self.HEIGHT))
        self.draw_rect(pos,(.78*self.WIDTH,-0.128*self.HEIGHT))
        cv2.putText(self.last_frame, "%s - ROUND %s %s"%(self.teamname, self.rn, "Free Routine" if self.mode == "F" else self.seq),  
                pos, font, 
                self.FONT_SCALER*1, (255, 255, 255), 
                self.FONT_SCALER*2, cv2.LINE_AA)
        pos = (round(.844*self.WIDTH), round(.064*self.HEIGHT))
        self.draw_rect(pos,(.156*self.WIDTH,-.064*self.HEIGHT))
        cv2.putText(self.last_frame, str(round(print_time.total_seconds(),1)),  
                pos, font, 
                self.FONT_SCALER*2, (255, 255, 255), 
                self.FONT_SCALER*7, cv2.LINE_AA)
        pts_color = (255,255,255)
        if print_point:
            cv2.circle(self.last_frame,
                    (round(.100*self.WIDTH), round(.9*self.HEIGHT)), self.FONT_SCALER*20, 
                    (0, 255 if self.key == "'+'" else 0, 0 if self.key == "'+'" else 255), 
                    self.FONT_SCALER*30)
            pos = (round(.156*self.WIDTH),round(.872*self.HEIGHT))
            cv2.putText(self.last_frame, "%s"%(self.key_dict[self.key]),
                    pos, font, 
                    self.FONT_SCALER*2, (0, 0, 255), 
                    self.FONT_SCALER*7, cv2.LINE_AA)
            pts_color = (0,0,255)
        if self.mode == 'C':
            # pos = (round(.898*self.WIDTH), round(.897*self.HEIGHT))
            pos = (round(.898*self.WIDTH), round(.97*self.HEIGHT))
            self.draw_rect(pos,(.156*self.WIDTH,-.096*self.HEIGHT))
            cv2.putText(self.last_frame, "%d"%(self.pts),
                    pos, font, 
                    self.FONT_SCALER*3, (255, 255, 255) if self.key == "'+'" else pts_color, 
                    # 3, (255, 0, 255), 
                    self.FONT_SCALER*10, cv2.LINE_AA)
        if print_final:
            pos = (round(.039*self.WIDTH),round(.513*self.HEIGHT))
            self.draw_rect(pos,(.859*self.WIDTH,-.417*self.HEIGHT))
            if self.mode == 'C':
                self.print_res(self.dstr[0],self.dstr[1:],font)
            if self.mode == 'F':
                self.print_res("style         dive_plan         camera (qual + prog)",self.strl,font)
                
            pos = (round(.234*self.WIDTH), round(.833*self.HEIGHT))
            self.draw_rect(pos,(.391*self.WIDTH,-.256*self.HEIGHT))
            cv2.putText(self.last_frame, "style: %.1f"%(self.style),
                    (round(.234*self.WIDTH), round(.641*self.HEIGHT)), font, 
                    self.FONT_SCALER*1, (255, 255, 255), 
                    self.FONT_SCALER*2, cv2.LINE_AA)
            if self.mode == 'F':
                cv2.putText(self.last_frame, "dive_plan: %.1f"%(self.dive_plan),
                        (round(.234*self.WIDTH), round(.705*self.HEIGHT)), font, 
                        self.FONT_SCALER*1, (255, 255, 255), 
                        self.FONT_SCALER*2, cv2.LINE_AA)
                cv2.putText(self.last_frame, "camera: %.1f"%(self.camera),
                        (round(.234*self.WIDTH), round(.769*self.HEIGHT)), font, 
                        self.FONT_SCALER*1, (255, 255, 255), 
                        self.FONT_SCALER*2, cv2.LINE_AA)
        if self.mode != "start":
            self.fout.write(self.last_frame)
        # else:
    def show_frame(self):
        if self.status:
            if self.mode == "start":
                cv2.imshow('frame', self.frame)
            # cv2.imshow('frame', self.frame)
            key = cv2.waitKey(round(self.FPS_MS))
            if self.mode == "start":
                if key == ord('/') and not self.start:
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
    args = parse_cmdline()
    # src = '../../output2.MP4'
    # src = 'https://videos3.earthcam.com/fecnetwork/9974.flv/chunklist_w1421640637.m3u8'
    threaded_camera = ThreadedVideo(args.source)
    while not threaded_camera.done:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass
    threaded_camera.join()
    