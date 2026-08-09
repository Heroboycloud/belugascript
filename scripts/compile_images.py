import os
from sound_effects import add_sounds


def gen_vid(filename):
    input_folder = '../chat/'
    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.png')])

    # Read durations from the file.
    durations = []
    with open(filename, encoding="utf8") as f:
        name_up_next = True

        lines = f.read().splitlines()
        for line in lines:
            if line == '':
                name_up_next = True
                continue
            elif line[0] == '#':
                continue
            elif line.startswith("WELCOME"):
                if "#!" in line:
                    durations.append(line.split('$^')[1].split("#!")[0])
                else:
                    durations.append(line.split('$^')[1])
                continue
            elif name_up_next:
                name_up_next = False
                continue
            else:
                if "#!" in line:
                    durations.append(line.split('$^')[1].split("#!")[0])
                else:
                    durations.append(line.split('$^')[1])

    # Create a text file to store the image paths.
    # The "ffconcat version 1.0" header is required - without it the concat
    # demuxer only understands plain "file" lines, and any other directive
    # (like "outpoint") fails with "unknown keyword". newline="\n" keeps
    # Windows from silently adding \r characters that can also break parsing.
    image_paths_file = os.path.join(os.getcwd(), 'scripts', 'image_paths.txt')
    with open(image_paths_file, 'w', encoding="utf8", newline="\n") as file:
        file.write("ffconcat version 1.0\n")
        for image_file in image_files:
            file.write(f"file '{input_folder}{image_file}'\n")
        file.write(f"file '{input_folder}{image_files[-1]}'\n")
        file.write("outpoint 0.04\n")

    video_width, video_height = 1280, 720
    ffmpeg_cmd = (
        f"ffmpeg -f concat -safe 0 -i scripts/image_paths.txt -vcodec libx264 -r 25 -crf 25 "
        f"-vf \"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2\" -pix_fmt yuv420p output.mp4"
    )
    print(ffmpeg_cmd)
    os.system(ffmpeg_cmd)
    # os.remove('image_paths.txt')

    add_sounds(filename)
