import glob
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

for file in os.listdir(OUTPUT_PATH):
    if file.endswith(".aiff"):
        input_file = os.path.join(OUTPUT_PATH, file)
        output_file = input_file.replace(".aiff", ".mp3")
        file_name = output_file.split("/")[-1]
        # convert to mp3; truncate after 369 seconds; last 3 seconds fade out
        cmd = f'sox "{input_file}" "{output_file}" fade h 0 369 3 '
        os.system(cmd)
        # add some id3 v1 and v2 tags
        cmd = f'id3tag -aiMproviser --album="iMproviser backingtracks" --song="iMproviser backing track {file_name}" ' \
              f'--desc="Comment=Copyright 2024, iMproviser, all rights reserved." --comment="Comment=Copyright 2024, ' \
              f'iMproviser, all rights reserved." "{output_file}"'
        os.system(cmd)
