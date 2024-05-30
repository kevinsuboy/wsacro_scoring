#!/usr/bin/env python

from threading import Thread
import time

class KeyStroker(Thread):
    def __init__(self):
        super().__init__()
        self.stop = False
        print(self.daemon)
    def run(self):
        while(not self.stop):
            time.sleep(1)
            print("running")
    def join(self):
        self.stop = True
        print("joined")
        super().join()




if __name__ == "__main__":
    print("hello world")
    ks_obj = KeyStroker()
    ks_obj.start()
    try:
        while(True):
            time.sleep(100)
    except KeyboardInterrupt:
        ks_obj.join()
    print("quit")
    quit()