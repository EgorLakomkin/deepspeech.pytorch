from __future__ import print_function

import fnmatch
import io
import os
import subprocess


def update_progress(progress):
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50),
                                                  progress * 100), end="")


def _get_transcription_path(wav_path):
    return wav_path.replace('/wav/', '/txt/').replace('.wav', '.txt')

def _get_duration(wav_file):
    output = subprocess.check_output(
        ['soxi -D \"%s\"' % wav_file.strip()],
        shell=True
    )
    return float(output)

def create_manifest(data_path, tag, ordered=True, add_duration=False):
    manifest_path = '%s_manifest.csv' % tag
    file_paths = []
    wav_files = [os.path.join(dirpath, f)
                 for dirpath, dirnames, files in os.walk(data_path)
                 for f in fnmatch.filter(files, '*.wav')]
    size = len(wav_files)
    counter = 0
    for file_path in wav_files:
        if not os.path.exists( _get_transcription_path(file_path) ):
            continue
        file_paths.append(file_path.strip())
        counter += 1
        update_progress(counter / float(size))
    print('\n')
    if ordered:
        _order_files(file_paths)
    counter = 0
    with io.FileIO(manifest_path, "w") as file:
        for wav_path in file_paths:
            transcript_path = _get_transcription_path(wav_path)
            if not add_duration:
                sample = os.path.abspath(wav_path) + ',' + os.path.abspath(transcript_path) + '\n'
            else:
                sample = os.path.abspath(wav_path) + ',' + os.path.abspath(transcript_path) +  ',' + str(_get_duration(wav_path)) +'\n'
            file.write(sample.encode('utf-8'))
            counter += 1
            update_progress(counter / float(size))
    print('\n')


def _order_files(file_paths):
    print("Sorting files by length...")

    file_paths.sort(key=_get_duration)
