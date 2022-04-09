"""
This script collects all chord files and builds a list of unique chord patterns it found.

It works on OUTPUT folders (e.g. when you runned the other scripts and added stuff you can re-generate the JS list)

It will output a python dict and JS that can be used to populate the mobile app constant:
`SCALE_PATTERNS_WITH_BACKING_TRACKS`

"""
import json
import os
import sys
from shutil import copyfile

import requests
import structlog

# Default to local running instance for now
OUTPUT_PATH1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
OUTPUT_PATH2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Scales Set 1 2022/output')

if not os.path.exists(OUTPUT_PATH1) or not os.path.exists(OUTPUT_PATH2):
    sys.exit('Error: Please ensure that both the output folders exist.')

root_keys = {
    "cis1": "C#", "fis1": "F#", "a1": "A", "c1": "C", "ees1": "Eb", "b1": "B", "bes1": "Bb", "aes1": "Ab", "d1": "D",
    "g1": "G", "e1": "E", "f1": "F"
}


def get_root_pitch(chord_pattern):
    chord = chord_pattern.split(" ")[0]
    if ":" in chord:
        chord = chord.split(":")[0]
    return chord


def get_mode(chord_pattern):
    mode = chord_pattern.split(" ")[0]
    if ":" in mode:
        mode = mode.split(":")[1]
        if mode == "m7":
            return "Minor 7"
        elif mode == "7":
            return "Dominant 7"
        elif mode == "maj7":
            return "Major 7"
        else:
            print(f"Unsupported mode: {chord_pattern}")
            sys.exit()
    else:
        mode = "Major"
    return mode


def extract_backing_track_name(file_name):
    name = " - ".join(file_name.split(" - ")[0:2])
    print(name)
    return name


def make_chord_dict_key(backing_track_name, pitch):
    return backing_track_name.lower().replace(" - ", "_").replace(" ", "_") + f"_{pitch}"


# build final dict
chord_dict = {}
skipped = 0
for file in os.listdir(OUTPUT_PATH1):
    if file.endswith(".txt"):
        with open(os.path.join(OUTPUT_PATH1, file), "r") as chord_reader:
            print(f"Handling {file}")
            chord_pattern = chord_reader.read()
            backing_track_name = extract_backing_track_name(file)
            backing_track_name_with_pitch = f"{backing_track_name} in {root_keys[get_root_pitch(chord_pattern)]}"
            key_name = make_chord_dict_key(backing_track_name, get_root_pitch(chord_pattern)[0:-1])
            print(chord_pattern)
            if key_name in chord_dict:
                print(f"Skipping {chord_pattern} as it already exists")
                skipped += 1
            else:
                chord_dict[key_name] = {"mode": get_mode(chord_pattern), "start_pitch": get_root_pitch(chord_pattern),
                                        "start_pitch_human": root_keys[get_root_pitch(chord_pattern)],
                                        "backing_track": "always", "multi_key": True,
                                        "name": backing_track_name_with_pitch, "chords": chord_pattern}

for file in os.listdir(OUTPUT_PATH2):
    if file.endswith(".txt"):
        with open(os.path.join(OUTPUT_PATH2, file), "r") as chord_reader:
            print(f"Handling {file}")
            chord_pattern = chord_reader.read()
            backing_track_name = extract_backing_track_name(file)
            backing_track_name_with_pitch = f"{backing_track_name} in {root_keys[get_root_pitch(chord_pattern)]}"
            key_name = make_chord_dict_key(backing_track_name, get_root_pitch(chord_pattern)[0:-1])
            print(chord_pattern)
            if key_name in chord_dict:
                print(f"Skipping {chord_pattern} as it already exists")
                skipped += 1
            else:
                chord_dict[key_name] = {"mode": get_mode(chord_pattern), "start_pitch": get_root_pitch(chord_pattern),
                                        "start_pitch_human": root_keys[get_root_pitch(chord_pattern)],
                                        "backing_track": "always", "multi_key": True,
                                        "name": backing_track_name_with_pitch.replace(" in ", " starts on "), "chords": chord_pattern}

print("Final dict")
chord_dict_list = [item[1] for item in chord_dict.items()]
json_list = json.dumps(chord_dict_list)
print(json_list)
print(f"Total items: {len(chord_dict.items())}, skipped: {skipped}")


print("\n\n********\nCLEANED UP JS OUTPUT:\n********\n\n")
cleaned_up = json_list.replace('"mode"', 'mode').replace('"start_pitch_human"', 'start_pitch_human')\
    .replace('"start_pitch"', 'start_pitch').replace('"backing_track"', 'backing_track').replace('"name"', 'name').replace('"chords"', 'chords').replace('"multi_key"', 'multi_key')
print(cleaned_up)

# root_keys = []
# for chord_pattern in unique_chord_patterns:
#     chord = chord_pattern.split(" ")[0]
#     if ":" in chord:
#         chord = chord.split(":")[0]
#     root_keys.append(chord)
# print(list(set(root_keys)))
