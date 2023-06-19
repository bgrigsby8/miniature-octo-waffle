#!/usr/bin/python3
"""
Main video editor script
"""

import moviepy.editor as mp
import numpy as np
from scipy.io import wavfile
import os
import re

BUFFER = 0.5  # seconds

def get_audio_file(video_file):
    """
    Extract the audio from a .mp4 file, and outputs
    into a .wav file
    """
    curr_directory = get_curr_directory()
    audio_file_path = "{}/tmp_audio.wav".format(curr_directory)
    video = mp.VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(audio_file_path, codec='pcm_s16le')

    return audio_file_path


def get_wav_data(audio_file):
    """
    Reads a .wav audio file and outputs the sample rate and audio data
    """
    sample_rate, audio_data = wavfile.read(audio_file)

    return sample_rate, audio_data

def calculate_threshold_dB(audio_data, sample_rate, duration):
    """
    Returns the ambient noise level in dB
    """
    filtered_audio_data = np.array([])
    for sample, data in enumerate(audio_data):
        sample_timestamp = sample / sample_rate
        if sample_timestamp <= duration:
            filtered_audio_data = np.append(filtered_audio_data, data[0])
        else:
            break

    filtered_audio_data = filtered_audio_data.astype(np.float32)
    positive_values = filtered_audio_data[filtered_audio_data >= 0]
    average_silence_dB = np.mean(positive_values)

    return average_silence_dB


def get_audiofile_duration(audio_data, sample_rate):
    """
    Uses the sample rate and audio data to determine the duration of the audio file
    """
    audio_duration = len(audio_data) / sample_rate
    return audio_duration

def get_timestamps(audio_data, sample_rate, silence_threshold):

    cut_samples = []
    for sample, amplitude in enumerate(audio_data):
        if abs(amplitude[0]) > silence_threshold:
            cut_samples.append(sample)

    timestamps = [sample / sample_rate for sample in cut_samples]
    return timestamps


def cut_video(input_file, output_file, start_time, end_time):
    """
    Cuts a .mp4 file around the provided timestamps
    """
    video = mp.VideoFileClip(input_file)

    cut_video = video.subclip(start_time, end_time)
    cut_video.write_videofile(output_file, codec="libx264", audio_codec="aac")


def timestamp_clips(timestamps, silence_duration, video_file, progress_callback=None, cancel_flag=None):
    curr_directory = get_curr_directory()
    create_tmp_directory()

    counter = 0
    total_clips = len(timestamps) - 1
    for i, timestamp in enumerate(timestamps):
        try:
            if timestamps[i + 1] - timestamp >= silence_duration:
                cut_video(video_file,
                          "{}/tmp/silence_from_{}_to_{}_seconds.mp4".format(curr_directory, round(timestamp, 2), round(timestamps[i + 1], 2)),
                          timestamp,
                          timestamps[i + 1]
                          )
                curr_start_silence_timestamp = timestamp + BUFFER
                counter += 1
                if counter == 1:
                    cut_video(video_file,
                              "{}/tmp/non_silence_from_{}_to_{}_seconds.mp4".format(curr_directory, "0", round(curr_start_silence_timestamp, 2)),
                              0,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1] - BUFFER
                elif counter > 1:
                    cut_video(video_file,
                              "{}/tmp/non_silence_from_{}_to_{}_seconds.mp4".format(curr_directory, round(prev_end_silence_timestamp, 2), curr_start_silence_timestamp),
                              prev_end_silence_timestamp,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1] - BUFFER

            progress = (i + 1) / total_clips * 100
            progress_callback(progress)
        except IndexError:
            break


def get_curr_directory():
    curr_directory = os.getcwd()
    return curr_directory


def create_tmp_directory():
    curr_directory = get_curr_directory()

    tmp_directory_path = "{}/tmp".format(curr_directory)
    if not os.path.exists(tmp_directory_path):
        os.mkdir(tmp_directory_path)


def combine_videos(delete_tmp):
    curr_directory = get_curr_directory()
    video_files = [f for f in os.listdir("{}/tmp".format(curr_directory)) if f.endswith('.mp4')]
    non_silence_video_files = [f for f in os.listdir("{}/tmp".format(curr_directory)) if f.endswith('.mp4') and 'non_silence' in f]
    non_silence_video_files = sorted(non_silence_video_files, key=lambda x: re.search(r'\d+', x).group())

    clips = []
    for non_silence_video_file in non_silence_video_files:
        clip = mp.VideoFileClip(os.path.join("{}/tmp".format(curr_directory), non_silence_video_file))
        clips.append(clip)
        os.remove(os.path.join("{}/tmp".format(curr_directory), non_silence_video_file))

    if clips:
        final_clip = mp.concatenate_videoclips(clips)
        final_clip.write_videofile("{}/output_video.mp4".format(curr_directory))

        final_clip.close()
        for clip in clips:
            clip.close()
        no_non_silence_videos = False
    else:
        no_non_silence_videos = True

    if delete_tmp == 1:
        for video_file in video_files:
            try:
                os.remove(os.path.join("{}/tmp".format(curr_directory), video_file))
            except FileNotFoundError:
                continue
        if len(os.listdir("{}/tmp".format(curr_directory))) == 0:
            os.rmdir("{}/tmp".format(curr_directory))

    os.remove(os.path.join("{}".format(curr_directory), "tmp_audio.wav"))

    if no_non_silence_videos == True:
        raise Exception("There were no silences longer than <duration> or below <threshold>")

def main(silence_duration, silence_threshold, video_file, delete_tmp, progress_callback=None):
    """
    Extracts the silences from a .mp4 from the silence parameters,
    and exports them as clips
    """
    audio_file_path = get_audio_file(video_file)
    # audio_file_path = "/home/deck"

    sample_rate, audio_data = get_wav_data(audio_file_path)

    if silence_threshold == 0:
        silence_threshold = calculate_threshold_dB(audio_data, sample_rate, 3) * 3

    silence_timestamps = get_timestamps(audio_data, sample_rate, silence_threshold=silence_threshold)
    timestamp_clips(silence_timestamps, silence_duration=silence_duration, video_file=video_file, progress_callback=progress_callback)
    combine_videos(delete_tmp)

    if progress_callback:
        progress_callback(100)
