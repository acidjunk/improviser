import glob
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

for file in os.listdir(OUTPUT_PATH):
    if file.endswith(".SGU") and "Bb" in file:
        input_file = os.path.join(OUTPUT_PATH, file)
        output_file = os.path.join(OUTPUT_PATH, file.replace("Bb", "Bes"))
        print(output_file)
        cmd = f'mv "{input_file}" "{output_file}"'
        # # print(cmd)
        os.system(cmd)
