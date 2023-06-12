"""
Main video editor script
"""

import moviepy.editor as mp
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import speech_recognition as sr

import trim_audio

VIDEO_FILE = "/home/deck/miniature-octo-waffle/VideoEditor/test_video.mp4"
AUDIO_FILE = "/home/deck/miniature-octo-waffle/VideoEditor/test_audio.wav"

def extract_audio(video_file, audio_file):
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return text

def filter_stopwords(text):
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text)
    filtered_words = [word for word in tokens if word.lower() not in stop_words]
    filtered_text = " ".join(filtered_words)
    return filtered_text

def main():
    extract_audio(VIDEO_FILE, AUDIO_FILE)
    transcribed_text = transcribe_audio(AUDIO_FILE)
    filtered_text = filter_stopwords(transcribed_text)
    print("Original Text: ".format(transcribed_text))
    print("Filtered Text: ".format(filtered_text))

if __name__ == "__main__":
    main()
