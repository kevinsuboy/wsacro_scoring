#!/usr/bin/env ipython

from moviepy.editor import *
import code

if __name__ == "__main__":
    clip = VideoFileClip("../../output.MP4")
    # clip.preview(fps=15, audio=False)
    clip.ipython_display(width=200)
    code.interact(locals=locals())