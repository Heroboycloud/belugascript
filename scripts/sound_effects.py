import os
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

my_folder = "C:/Users/Debugger/Desktop/codes/Text-2-Beluga"


def get_sound_path(sound_name):
    """
    Build the full path to the sound file and verify that it exists.
    """
    sound_name = sound_name.strip()

    # If the script accidentally includes .mp3 already, avoid name.mp3.mp3
    if sound_name.lower().endswith(".mp3"):
        sound_name = sound_name[:-4]

    sound_dir = Path(my_folder) / "assets" / "sounds" / "mp3"
    sound_path = sound_dir / f"{sound_name}.mp3"

    if not sound_path.exists():
        available = []
        if sound_dir.exists():
            available = sorted(p.name for p in sound_dir.glob("*.mp3"))

        raise FileNotFoundError(
            "Could not find sound file.\n"
            f"Parsed sound name: {sound_name!r}\n"
            f"Expected path: {sound_path}\n"
            f"Sound folder exists: {sound_dir.exists()}\n"
            f"Available MP3 files: {available}"
        )

    return str(sound_path)


def parse_duration_and_sound(line):
    """
    Parse lines like:

        some text $^2.5
        some text $^2.5#!pop

    Returns:
        duration_part, sound_name_or_None
    """
    if "$^" not in line:
        raise ValueError(f"Line is missing '$^' duration marker: {line!r}")

    after_marker = line.split("$^", 1)[1]

    if "#!" in after_marker:
        duration_part, sound_part = after_marker.split("#!", 1)
        return duration_part.strip(), sound_part.strip()

    return after_marker.strip(), None


def add_sounds(filename):
    video_path = Path(my_folder) / "output.mp4"

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    video = VideoFileClip(str(video_path))

    duration = 0.0
    audio_clips = []

    with open(filename, encoding="utf8") as f:
        name_up_next = True

        for line in f.read().splitlines():
            if line == "":
                name_up_next = True
                continue

            if line.startswith("#"):
                continue

            if line.startswith("WELCOME"):
                duration_part, sound_part = parse_duration_and_sound(line)

                if sound_part:
                    audio_file = get_sound_path(sound_part)
                    audio_clip = AudioFileClip(audio_file).set_start(duration)
                    audio_clips.append(audio_clip)

                duration += float(duration_part)
                continue

            if name_up_next:
                name_up_next = False
                continue

            duration_part, sound_part = parse_duration_and_sound(line)

            if sound_part:
                audio_file = get_sound_path(sound_part)
                audio_clip = AudioFileClip(audio_file).set_start(duration)
                audio_clips.append(audio_clip)

            duration += float(duration_part)

    if audio_clips:
        composite_audio = CompositeAudioClip(audio_clips)
        video = video.set_audio(composite_audio)

    final_video_path = Path(my_folder) / "final_video.mp4"

    video.write_videofile(
        str(final_video_path),
        codec="libx264",
        audio_codec="aac"
    )