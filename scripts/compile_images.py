import os
import subprocess
from sound_effects import add_sounds

my_folder = r"C:/Users/Debugger/Desktop/codes/Text-2-Beluga"


def parse_durations(filename):
    durations = []

    with open(filename, encoding="utf8") as f:
        name_up_next = True
        lines = f.read().splitlines()

        for line in lines:
            if line == "":
                name_up_next = True
                continue

            if line.startswith("#"):
                continue

            if line.startswith("WELCOME"):
                if "$^" not in line:
                    raise ValueError(f"WELCOME line missing '$^' duration: {line!r}")

                duration_part = line.split("$^", 1)[1]

                if "#!" in duration_part:
                    duration_part = duration_part.split("#!", 1)[0]

                durations.append(duration_part.strip())
                continue

            if name_up_next:
                name_up_next = False
                continue

            if "$^" not in line:
                raise ValueError(f"Message line missing '$^' duration: {line!r}")

            duration_part = line.split("$^", 1)[1]

            if "#!" in duration_part:
                duration_part = duration_part.split("#!", 1)[0]

            durations.append(duration_part.strip())

    return durations


def gen_vid(filename):
    input_folder = os.path.join(my_folder, "chats")

    image_files = sorted(
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".png")
    )

    if not image_files:
        raise FileNotFoundError(f"No PNG images found in: {input_folder}")

    durations = parse_durations(filename)

    if len(durations) != len(image_files):
        raise ValueError(
            f"Found {len(image_files)} images but parsed {len(durations)} "
            f"durations from the script - they must match 1:1. Check the "
            f"script formatting (every WELCOME/message line needs '$^<seconds>')."
        )

    # We write the concat file to the project folder...
    concat_abs = os.path.join(my_folder, "image_paths.txt")

    # ...but inside the concat file we use RELATIVE paths.
    with open(concat_abs, "w", encoding="utf8", newline="\n") as file:
        file.write("ffconcat version 1.0\n")

        for image_file, dur in zip(image_files, durations):
            file.write(f"file 'chats/{image_file}'\n")
            file.write(f"duration {float(dur.strip())}\n")

        # Repeat the last file so its duration is honored.
        file.write(f"file 'chats/{image_files[-1]}'\n")

    if not os.path.exists(concat_abs):
        raise FileNotFoundError(f"Failed to create concat file: {concat_abs}")

    video_width, video_height = 1280, 720

    vf = (
        f"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2"
    )

    # Use relative paths for the ffmpeg input/output too.
    # cwd=my_folder makes this safe.
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "image_paths.txt",
        "-vcodec", "libx264",
        "-r", "25",
        "-crf", "25",
        "-vf", vf,
        "-pix_fmt", "yuv420p",
        "output.mp4",
    ]

    print("Running ffmpeg from cwd:")
    print(my_folder)
    print()
    print("ffmpeg command:")
    print(subprocess.list2cmdline(ffmpeg_cmd))
    print()
    print("image_paths.txt contents:")
    with open(concat_abs, encoding="utf8") as f:
        print(f.read())

    subprocess.run(ffmpeg_cmd, check=True, cwd=my_folder)

    output_abs = os.path.join(my_folder, "output.mp4")

    if not os.path.exists(output_abs):
        raise FileNotFoundError(f"ffmpeg did not create expected output file: {output_abs}")

    if os.path.getsize(output_abs) == 0:
        raise RuntimeError(f"ffmpeg created an empty output file: {output_abs}")

    add_sounds(filename)



