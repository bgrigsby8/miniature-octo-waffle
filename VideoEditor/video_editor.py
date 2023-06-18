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

VIDEO_FILE = "/home/deck/miniature-octo-waffle/VideoEditor/test_video.mp4"
AUDIO_FILE = "/home/deck/miniature-octo-waffle/VideoEditor/test_audio.wav"
SILENCE_THRESHOLD = 1500
SILENCE_DURATION = 1.0

class VideoEditor:
    def __init__(self, video_file):
        self.video_file = video_file

    def get_audio_file(video_file):
        video = mp.VideoFileClip(video_file)

        # Extract the audio from the video
        audio = video.audio

        # Save the audio as a WAV file
        audio.write_audiofile(AUDIO_FILE, codec='pcm_s16le')

    def get_wav_data(self):
        """
        Reads a .wav audio file and outputs the sample rate and audio data
        """
        VideoEditor.get_audio_file(VIDEO_FILE)
        self.sample_rate, self.audio_data = wavfile.read(AUDIO_FILE)
        return self.sample_rate, self.audio_data

    def transcribe_audio(self):
        """
        Input: An audio file, perferably in the form of a .wav file

        Output: String containing transcribed text

        Note: This function uses the Google Speech-to-text language model.
        You can play around with different language models to see which one
        works best, but I found the Google one to be the most accurate
        """
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = RECOGNIZER_SILENCE_THRESHOLD
        recognizer.pause_threshold = RECOGNIZER_PAUSE_THRESHOLD

        engines = ["google", "sphinx"]

        for engine in engines:
            try:
                with sr.AudioFile(self.audio_file) as source:
                    audio = recognizer.record(source)
                if engine == "google":
                    google_text = recognizer.recognize_google(audio, show_all=True)
                    return google_text
            except sr.UnknownValueError:
                return "Recognition could not understand audio"
            except sr.RequestError as e:
                return "Could not request results from {} engine; {}".format(engine, e)

    def filter_stopwords(text):
        """
        Input: Transcribed text from a .wav file

        Output: A string filtering out uneccessary words
        """
        stop_words = set(stopwords.words("english"))
        tokens = word_tokenize(text)
        filtered_words = [word for word in tokens if word.lower() not in stop_words]
        filtered_text = " ".join(filtered_words)
        return filtered_text

    def get_word_timings(transcribed_text):
        """
        Input: Transcribed text and outputs the word timings,
        these timings are from the SpeechRecognition library

        Output: Timings between each word
        """
        word_timings = []
        for alternative in transcribed_text["alternative"]:
            for word in alternative["words"]:
                start_time = word["start_time:"]
                end_time = word["end_time"]
                word_timings.append((start_time, end_time))

        return word_timings

def get_audio_file(video_file):
    """
    Extract the audio from a .mp4 file, and outputs
    into a .wav file
    """
    video = mp.VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(AUDIO_FILE, codec='pcm_s16le')

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
    counter = 0
    for i, timestamp in enumerate(timestamps):
        try:
            if silence == True and timestamps[i + 1] - timestamp >= SILENCE_DURATION:
                cut_video(VIDEO_FILE,
                          "/home/deck/miniature-octo-waffle/VideoEditor/silence_from_{}_to_{}_seconds.mp4".format(round(timestamp, 2), round(timestamps[i + 1], 2)),
                          timestamp,
                          timestamps[i +1]
                          )
                curr_start_silence_timestamp = timestamp
                counter += 1
                if counter == 1:
                    cut_video(VIDEO_FILE,
                              "/home/deck/miniature-octo-waffle/VideoEditor/non_silence_from_{}_to_{}_seconds.mp4".format("0", round(curr_start_silence_timestamp, 2)),
                              0,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1]
                elif counter > 1:
                    cut_video(VIDEO_FILE,
                              "/home/deck/miniature-octo-waffle/VideoEditor/non_silence_from_{}_to_{}_seconds.mp4".format(round(prev_end_silence_timestamp, 2), curr_start_silence_timestamp, 2),
                              prev_end_silence_timestamp,
                              curr_start_silence_timestamp
                              )
                    prev_end_silence_timestamp = timestamps[i + 1]
        except IndexError:
            break
def main():
    """
    Extracts the silences from a .mp4 from the silence parameters,
    and exports them as clips
    """
    get_audio_file(VIDEO_FILE)

    sample_rate, audio_data = get_wav_data(AUDIO_FILE)
    silence_timestamps = get_timestamps(audio_data, sample_rate, silence=True)
    timestamp_clips(silence_timestamps, silence=True)



if __name__ == "__main__":
    main()
