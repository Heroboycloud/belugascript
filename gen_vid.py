from moviepy.editor import *
clip=ColorClip(size=(1920,1080),color=(0,0,0),duration=5)
clip.write_videofile('output.mp4',fps=24)
