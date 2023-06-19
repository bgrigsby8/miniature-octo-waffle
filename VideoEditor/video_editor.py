"""
Main video editor script
"""

import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import speech_recognition as sr
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import sys
import os
import re

#Arguments from GUI
SILENCE_DURATION = int(sys.argv[1]) if sys.argv[1] else 2
SILENCE_THRESHOLD = int(sys.argv[2]) if sys.argv[2] else 1500
VIDEO_FILE = str(sys.argv[3])

BUFFER = 0.5 #seconds

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

def plot(audio_data, audio_duration):
    """
    Uses the audio_data and audio_duration to plot the audio waves
    """
    time = np.linspace(0, audio_duration, len(audio_data))

    #Plot the waveform
    plt.figure(figsize=(10, 4))
    plt.plot(time, audio_data)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Waveform")
    plt.show()

def get_audiofile_duration(audio_data, sample_rate):
    """
    Uses the sample rate and audio data to determine the duration of the audio file
    """
    audio_duration = len(audio_data) / sample_rate
    return audio_duration

def get_silence_timestamps(audio_data, sample_rate):

    silence_samples = []
    for sample, amplitude in enumerate(audio_data):
        if abs(amplitude[0]) > SILENCE_THRESHOLD:
            silence_samples.append(sample)

    silence_timestamps = [sample / sample_rate for sample in silence_samples]
    return silence_timestamps

def get_timestamps(audio_data, sample_rate, silence=False):

    samples = []
    for sample, amplitude in enumerate(audio_data):
        if silence == True and abs(amplitude[0]) > SILENCE_THRESHOLD:
            samples.append(sample)
        elif silence == False:
            samples.append(sample)

    timestamps = [sample / sample_rate for sample in samples]
    return timestamps

def cut_video(input_file, output_file, start_time, end_time):
    """
    Cuts a .mp4 file around the provided timestamps
    """
    video = mp.VideoFileClip(input_file)

    cut_video = video.subclip(start_time, end_time)
    cut_video.write_videofile(output_file, codec="libx264", audio_codec="aac")

def timestamp_clips(timestamps, silence=False):
    """
    Uses the silence timestamps to outputs .mp4 files of the silences
    from the original video
    """
    curr_directory = get_curr_directory()
    create_tmp_directory()

    counter = 0
    for i, timestamp in enumerate(timestamps):
        try:
            if silence == True and timestamps[i + 1] - timestamp >= SILENCE_DURATION:
                cut_video(VIDEO_FILE,
                          "{}/tmp/silence_from_{}_to_{}_seconds.mp4".format(curr_directory, round(timestamp, 2), round(timestamps[i + 1], 2)),
                          timestamp,
                          timestamps[i +1]
                          )
                curr_start_silence_timestamp = timestamp + BUFFER
                counter += 1
                if counter == 1:
                    cut_video(VIDEO_FILE,
                              "{}/tmp/non_silence_from_{}_to_{}_seconds.mp4".format(curr_directory, "0", round(curr_start_silence_timestamp, 2)),
                              0,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1] - BUFFER
                elif counter > 1:
                    cut_video(VIDEO_FILE,
                              "{}/tmp/non_silence_from_{}_to_{}_seconds.mp4".format(curr_directory, round(prev_end_silence_timestamp, 2), curr_start_silence_timestamp),
                              prev_end_silence_timestamp,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1] - BUFFER
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

def combine_videos():
    """
    Combines all the non_silence .mp4 files into one file, and outputs
    them in the cwd
    """
    curr_directory = get_curr_directory()
    video_files = [f for f in os.listdir("{}/tmp".format(curr_directory)) if f.endswith('.mp4') and 'non_silence' in f]
    print(video_files)
    video_files = sorted(video_files, key=lambda x: re.search(r'\d+', x).group())
    print(video_files)

    clips = []
    for video_file in video_files:
        # Load each video file
        clip = mp.VideoFileClip(os.path.join("{}/tmp".format(curr_directory), video_file))
        clips.append(clip)

    # Concatenate the video clips
    final_clip = mp.concatenate_videoclips(clips)

    # Write the final merged video to the output file
    final_clip.write_videofile("{}/output_video.mp4".format(curr_directory))

    # Close the video clips
    final_clip.close()
    for clip in clips:
        clip.close()

def main():
    """
    Extracts the silences from a .mp4 from the silence parameters,
    and exports them as clips
    """
    audio_file_path = get_audio_file(VIDEO_FILE)

    sample_rate, audio_data = get_wav_data(audio_file_path)
    silence_timestamps = get_timestamps(audio_data, sample_rate, silence=True)
    timestamp_clips(silence_timestamps, silence=True)
    combine_videos()



if __name__ == "__main__":
    main()
