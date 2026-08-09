import curses
import datetime
import sys
import textwrap
import os
from playsound import playsound

# Import functions directly from the modules.
from generate_chat import get_filename as get_chat_filename, save_images
from compile_images import gen_vid
from script_validator import get_filename as get_validator_filename, validate_script_lines

# Try to import pyfiglet for cool ASCII art. Fallback gracefully if not available.
try:
    from pyfiglet import figlet_format
except ImportError:
    def figlet_format(text):
        return text.upper()


from pathlib import Path
# ... other imports ...
# Define absolute paths based on this script's location
SCRIPT_DIR = Path(__file__).parent.resolve()
my_folder="C:/Users/Debugger/Desktop/codes/Text-2-Beluga"

BASE_DIR = SCRIPT_DIR.parent.resolve()

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"
CHAT_DIR = BASE_DIR / "chat"
OUTPUT_FILE = BASE_DIR / "output.mp4"








# Safe wrapper around addstr that never lets curses crash the program.
# Curses raises curses.error if you write past the edge of the screen or
# into the bottom-right cell, so every write must be clipped and guarded.
def safe_addstr(stdscr, y, x, text, attr=0):
    height, width = stdscr.getmaxyx()

    # Nothing to draw, or we've already run out of vertical space.
    if y < 0 or y >= height or x < 0 or x >= width:
        return

    # Clip horizontally so the string can never overflow the line.
    max_len = width - x
    # Curses can't draw into the very last cell of the screen (bottom-right
    # corner) without raising an error, so leave that one cell alone.
    if y == height - 1:
        max_len -= 1
    if max_len <= 0:
        return

    text = text[:max_len]
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        # Any other edge case (odd terminal, resize mid-draw, etc.) -
        # just skip this line instead of crashing the whole app.
        pass


# Pick a figlet font that's short enough to fit the current terminal height;
# fall back to plain text if even the smallest font won't fit.
def render_header(header, available_height):
    for font in ("standard", "small", "mini"):
        try:
            text = figlet_format(header, font=font)
        except Exception:
            continue
        lines = text.splitlines()
        if len(lines) <= available_height:
            return lines
    # Nothing fit - just use the plain header text.
    return [header]


# Helper function to update header and description in a dedicated screen area.
def draw_screen(stdscr, header, description, menu_items=None, current_row=None, left_margin=4):
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    # Leave some breathing room; if the terminal is tiny, don't bother
    # trying to fit a giant ASCII-art header.
    left_margin = min(left_margin, max(width - 1, 0))

    y = 1
    if height > 4:
        header_lines = render_header(header, max(height - 3, 1))
        for line in header_lines:
            if y >= height:
                break
            safe_addstr(stdscr, y, left_margin, line, curses.color_pair(1))
            y += 1
    else:
        safe_addstr(stdscr, 0, 0, header, curses.color_pair(1))
        y = 1

    # Wrap description text to fit the width with left margin = right margin = 4.
    desc_width = max(width - left_margin * 2, 1)
    wrapped_desc = textwrap.fill(description, width=desc_width)
    for line in wrapped_desc.splitlines():
        if y >= height:
            break
        safe_addstr(stdscr, y, left_margin, line, curses.color_pair(3))
        y += 1

    # If a menu is provided, render it.
    if menu_items is not None:
        y += 1
        for idx, item in enumerate(menu_items):
            if y >= height:
                break
            if idx == current_row:
                safe_addstr(stdscr, y, left_margin, f"> {item}", curses.color_pair(2))
            else:
                safe_addstr(stdscr, y, left_margin, f"  {item}", curses.color_pair(3))
            y += 1

    stdscr.refresh()


def run_generate_chat(stdscr):
    left_margin = 4
    # Initial header and description.
    draw_screen(stdscr, "Text 2 Beluga", "Select a chat script file...\n\n", menu_items=[])
    curses.napms(500)
    
    final_video = os.path.join(my_folder,'final_video.mp4')
    if os.path.isfile(final_video):
        os.remove(final_video)
    if os.path.exists(os.path.join(my_folder,'chat')):
        for file in os.listdir(os.path.join(my_folder,'chat')):
            os.remove(os.path.join(my_folder,'chat', file))
        os.rmdir(os.path.join(my_folder,'chat'))

    filename = get_chat_filename()
    if not filename:
        draw_screen(stdscr, "No Selection", "Press Enter to return to the main menu...\n\n", menu_items=[])
        stdscr.getch()
        return

    try:
        with open(filename, encoding="utf8") as f:
            lines = f.read().splitlines()
    except Exception as e:
        draw_screen(stdscr, "Error", f"{e}\nPress Enter to return to the main menu...\n\n", menu_items=[])
        stdscr.getch()
        return

    current_time = datetime.datetime.now()

    # Step 1: Generating Chats
    draw_screen(stdscr, "Reading Chats...", "Please wait while chat images are being generated...\n\n", menu_items=[])
    stdscr.refresh()
    save_images(lines, init_time=current_time)

    # Step 2: Compiling Video
    draw_screen(stdscr, "Compiling Video...", "Compiling images into video. Please wait...\n\n", menu_items=[])
    stdscr.refresh()
    gen_vid(filename)  # Note: gen_vid internally calls add_sounds as needed.

    # Final message.
    draw_screen(stdscr, "Completed!", "Your Beluga-like video has been generated. Enjoy :)\nPress Enter to return to the main menu...\n\n", menu_items=[])
    stdscr.getch()


def run_validate_script(stdscr):
    left_margin = 4
    draw_screen(stdscr, "Text 2 Beluga", "Select a script file to validate...\n\n", menu_items=[])
    curses.napms(500)

    filename = get_validator_filename()
    if not filename:
        draw_screen(stdscr, "No Selection", "Press Enter to return to the main menu...\n\n", menu_items=[])
        stdscr.getch()
        return

    try:
        with open(filename, encoding="utf8") as f:
            lines = f.read().splitlines()
    except Exception as e:
        draw_screen(stdscr, "Error", f"{e}\nPress Enter to return to the main menu...\n\n", menu_items=[])
        stdscr.getch()
        return

    # Show "Validating..." header
    draw_screen(stdscr, "Validating...", "Please wait while the script is being validated...\n\n", menu_items=[])
    stdscr.refresh()
    curses.napms(500)

    errors = validate_script_lines(lines)
    if errors:
        header = "Errors"
        description = "Script validation found issues:\n" + "\n".join(errors)
    else:
        header = "Seems Good!"
        description = "Script validation successful: no problems found."

    draw_screen(stdscr, header, description + "\n\nPress Enter to return to the main menu...\n\n", menu_items=[])
    stdscr.getch()
    
################################################
################################################
################################################
################################################
    
def print_instructions(stdscr, header, description, current_row, left_margin):
    menu_items = ["Proper Script Formatting", "Available Sound Effects", "< Back"]
    while True:
        draw_screen(stdscr, header, description, menu_items, current_row, left_margin)
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord('k')]:
            current_row = (current_row - 1) % len(menu_items)
        elif key in [curses.KEY_DOWN, ord('j')]:
            current_row = (current_row + 1) % len(menu_items)
        elif key in [curses.KEY_ENTER, 10, 13]:
            if current_row == 0:
                formatting(stdscr, current_row, left_margin)
            elif current_row == 1:
                sounds(stdscr, current_row, left_margin)
            elif current_row == 2:
                break

def formatting(stdscr, current_row, left_margin):
    menu_items = [
        "--IMPORTANT__POINTS--",
        "- Any custom characters should be configured in [assets/profile_pictures/characters.json] and their profile pictures should be present.",
        "- All the dependencies listed in [requirements.txt] should be installed.",
        "",
        "--FORMATTING__GUIDELINES--",
        "- Lines beginning with a hashtag (#) are treated as comments and are ignored.",
        "- To display a \"character joined\" message, the line should begin with WELCOME followed by the character name ~ [WELCOME CharacterName]",
        "- To make a character say something, Write the character's name immediately followed by a colon and it's messages in the subsequent lines.",
        "- Each message should be (MANDATORILY) immediately followed by \"$^\" and a number that indicated for how many seconds that message should be shown.",
        "- Each duration can be (OPTIONALLY) immediately followed by \"#!\" and a sound effect name to play that sound in the video when that message is shown.",
        "- There should be an empty line between a character's message and the next character's name.",
        "- Message text enclosed within ** and ** will be shown in bold.",
        "- Message text enclosed within __ and __ will be shown in italics.",
        "- Emojis are supported in messages.",
        "- Different characters can be mentioned in a message by writing \"@\" followed by a character's name.",
        "",
        "- An example script has been provided to give an idea and get you started.",
        "",
        "< Back"
    ]
    header = "Formatting"
    description = "> Your chat script should be written in a [.txt] file with the following formatting guidelines:"
    
    while True:
        draw_screen(stdscr, header, description, menu_items, current_row, left_margin)
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord('k')]:
            current_row = (current_row - 1) % len(menu_items)
        elif key in [curses.KEY_DOWN, ord('j')]:
            current_row = (current_row + 1) % len(menu_items)
        elif key in [curses.KEY_ENTER, 10, 13]:
            if current_row == (len(menu_items) - 1):
                break
            
def sounds(stdscr, current_row, left_margin):
    header = "Sounds"
    description = "> Use the arrow keys to navigate through the available sound effects. Press [ENTER] to listen to the selected sound effect."
    
    menu_items = []
    for file in os.listdir(os.path.join(my_folder, "assets", "sounds", "mp3")):
        if file.endswith(".mp3"):
            menu_items.append(file.replace(".mp3", ""))
    menu_items.append("< ignore")
    menu_items.append("< Back")
    
    while True:
        draw_screen(stdscr, header, description, menu_items, current_row, left_margin)
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord('k')]:
            current_row = (current_row - 1) % len(menu_items)
        elif key in [curses.KEY_DOWN, ord('j')]:
            current_row = (current_row + 1) % len(menu_items)
        elif key in [curses.KEY_ENTER, 10, 13]:
            if current_row == (len(menu_items) - 1):
                break
            elif current_row == (len(menu_items) - 2):
                continue
            else:
                playsound(f'{os.path.join(my_folder, "assets", "sounds", "mp3", menu_items[current_row] + ".mp3")}')

################################################
################################################
################################################
################################################

def curses_menu(stdscr):
    # Hide the cursor and initialize colors. Some terminals (e.g. certain
    # Termux/Android setups) don't support cursor visibility changes or
    # full color - don't let that crash the app.
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    try:
        curses.start_color()
        # Color pairs:
        # Pair 1: Header (magenta on black)
        # Pair 2: Highlighted menu item (black on magenta)
        # Pair 3: Normal text (white on black)
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    except curses.error:
        pass

    menu_items = ["Generate Video", "Validate Script", "Instructions", "", "Exit"]
    current_row = 0
    left_margin = 4

    while True:
        # Draw main menu screen.
        header = "Text 2 Beluga"
        description = "> Welcome to Text2Beluga! Easily generate a Beluga-like video from a simple text file script within seconds. The best part? It's absolutely free!"
        draw_screen(stdscr, header, description, menu_items, current_row, left_margin)
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord('k')]:
            current_row = (current_row - 1) % len(menu_items)
        elif key in [curses.KEY_DOWN, ord('j')]:
            current_row = (current_row + 1) % len(menu_items)
        elif key in [curses.KEY_ENTER, 10, 13]:
            if current_row == 0:
                run_generate_chat(stdscr)
            elif current_row == 1:
                run_validate_script(stdscr)
            elif current_row == 2:
                print_instructions(stdscr, header, description, current_row, left_margin)
            elif current_row == 4:
                break
        # Loop again to redraw the menu.


def main():
    curses.wrapper(curses_menu)


if __name__ == '__main__':
    main()
