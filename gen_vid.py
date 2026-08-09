from moviepy.editor import *
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'output.mp4')

clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=5)
clip.write_videofile(output_path, fps=24)
print(f"Video created at: {output_path}")
