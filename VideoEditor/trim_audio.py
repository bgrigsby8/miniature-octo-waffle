"""
Reads an audio file, interprets the words from the file, and outputs
a trimmed transcript removing filler words
"""

import speech_recognition as sr
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

AUDIO_FILE_PATH = "/home/deck/miniature-octo-waffle/VideoEditor/test_audio.wav"

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
    audio_file = AUDIO_FILE_PATH
    transcribed_text = transcribe_audio(audio_file)
    filtered_text = filter_stopwords(transcribed_text)
    print("Original Text: ".format(transcribed_text))
    print("Filtered Text: ".format(filtered_text))

if __name__ == "__main__":
    main()
