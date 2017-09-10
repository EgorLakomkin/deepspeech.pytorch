from __future__ import print_function

import argparse
import io
import os

import subprocess

from utils import update_progress

parser = argparse.ArgumentParser(description='Merges all manifest CSV files in specified folder.')
parser.add_argument('--merge_dir', default='manifests/', help='Path to all manifest files you want to merge')
parser.add_argument('--min_duration', default=-1, type=int,
                    help='Optionally prunes any samples shorter than the min duration (given in seconds, default off)')
parser.add_argument('--max_duration', default=-1, type=int,
                    help='Optionally prunes any samples longer than the max duration (given in seconds, default off)')
parser.add_argument('--output_path', default='merged_manifest.csv', help='Output path to merged manifest')

args = parser.parse_args()

files = []
for file in os.listdir(args.merge_dir):
    if file.endswith(".csv"):
        with open(os.path.join(args.merge_dir, file), 'r') as fh:
            files += fh.readlines()

prune_min = args.min_duration >= 0
prune_max = args.max_duration >= 0
if prune_min:
    print("Pruning files with minimum duration %d" % (args.min_duration))
if prune_max:
    print("Pruning files with  maximum duration of %d" % (args.max_duration))

new_files = []
size = len(files)
for x in range(size):
    file_path = files[x]
    sample_info = file_path.strip().split(",")
    if len(sample_info) < 3:
        #duration is not present in this sample
        file_path = file_path.strip().split(',')[0]
        output = subprocess.check_output(
            ['soxi -D \"%s\"' % file_path.strip()],
            shell=True
        )
        duration = float(output)
    else:
        duration = float(sample_info[-1])
    if prune_min or prune_max:
        duration_fit = True
        if prune_min:
            if duration < args.min_duration:
                duration_fit = False
        if prune_max:
            if duration > args.max_duration:
                duration_fit = False
        if duration_fit:
            new_files.append((sample_info[0], sample_info[1], duration))
    else:
        new_files.append((sample_info[0], sample_info[1], duration))
    update_progress(x / float(size))

print("\nSorting files by length...")


def func(element):
    return element[2]


new_files.sort(key=func)

print("Saving new manifest...")

with io.FileIO(args.output_path, 'w') as f:
    for wav_file, txt_file, duration in new_files:
        sample = wav_file + ',' + txt_file + ',' + str(duration) + '\n'
        f.write(sample.encode('utf-8'))