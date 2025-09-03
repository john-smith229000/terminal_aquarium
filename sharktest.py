import time
import re
import sys

def load_frames(filepath, marker="-SHARK-", total_frames=26):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Start from marker
    start = content.find(marker)
    if start == -1:
        raise ValueError(f"Marker {marker} not found in file.")

    shark_content = content[start:]

    # Extract frames with regex
    pattern = re.compile(r"frame \d+\n(.*?)(?=\nframe|\Z)", re.DOTALL)
    matches = pattern.findall(shark_content)

    return matches[:total_frames]

def animate(frames, delay=0.15):
    try:
        while True:
            for i, frame in enumerate(frames, start=1):
                # clear screen
                print("\033[H\033[J", end="")

                # print frame
                print(frame, end="\n")

                # print frame number on its own line
                print(f"[Frame {i}/{len(frames)}]")

                # flush to make sure delay is respected
                sys.stdout.flush()

                # wait
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\nAnimation stopped.")

if __name__ == "__main__":
    frames = load_frames("mockups.txt")
    animate(frames, delay=0.2)  # change delay here
