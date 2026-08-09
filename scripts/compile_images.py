import os
from sound_effects import add_sounds


def gen_vid(filename):
    #input_folder at parent folder/assets/chat
    input_folder = os.path.join(os.getcwd(),'chat')
    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.png')])

    # Read the per-message durations (in seconds) from the script file.
    # These line up 1:1 with image_files, since save_images() in
    # generate_chat.py creates exactly one PNG per WELCOME/message line
    # using this same line-by-line logic. sound_effects.py later re-parses
    # this same script and sums these durations to time each sound effect,
    # so the video needs to actually honor them or the audio drifts.
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

    if len(durations) != len(image_files):
        raise ValueError(
            f"Found {len(image_files)} images but parsed {len(durations)} "
            f"durations from the script - they must match 1:1. Check the "
            f"script formatting (every WELCOME/message line needs '$^<seconds>')."
        )

    # Build the ffconcat script. Each image gets an explicit "duration" so
    # it stays on screen for the number of seconds specified in the script,
    # instead of relying on a flat "outpoint" hack that some ffmpeg builds
    # don't recognize at all. Per the concat demuxer docs, the duration of
    # the LAST file is ignored unless that file is listed again afterward -
    # hence the repeated final line (no duration needed on it).
    # Use absolute path for the concat file to avoid working directory issues
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    image_paths_file = os.path.join(scripts_dir, 'image_paths.txt')
    # Use absolute path for the chat folder and normalize it
    input_folder_abs = os.path.normpath(os.path.join(scripts_dir, '..', 'chat'))
    
    with open(image_paths_file, 'w', encoding="utf8", newline="\n") as file:
        file.write("ffconcat version 1.0\n")
        for i, (image_file, dur) in enumerate(zip(image_files, durations)):
            image_path = os.path.normpath(os.path.join(input_folder_abs, image_file))
            file.write(f"file '{image_path}'\n")
            # Don't write duration for the last image (it will be repeated)
            if i < len(image_files) - 1:
                file.write(f"duration {float(dur.strip())}\n")
        # Repeat the last file so its duration is honored
        last_image_path = os.path.normpath(os.path.join(input_folder_abs, image_files[-1]))
        file.write(f"file '{last_image_path}'\n")

    video_width, video_height = 1280, 720
    ffmpeg_cmd = (
        f"ffmpeg -y -f concat -safe 0 -i \"{image_paths_file}\" -vcodec libx264 -r 25 -crf 25 "
        f"-vf \"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2\" -pix_fmt yuv420p output.mp4"
    )
    print(ffmpeg_cmd)
    os.system(ffmpeg_cmd)
    # os.remove('image_paths.txt')

    add_sounds(filename)
