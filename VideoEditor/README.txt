=== Video Editor ===
Contributors: bgrigsby8
Version: 1.0

=== Description ===
Video editor lets you interact with a GUI, with multiple input fields in order to cut the silences
from you video. It does this by using time and silence threshold values, where time is the amount
of time in between non-silences to be considered silence, and silence threshold is a value to
determine what is considered silence, or ambient noise, in your video.

The GUI allows you to input the time, which has a default value of 2 seconds, the silence threshold,
which has a default value of 1500, a button to enable 'Dynamically Adjust Threshold', which listens
to the first 3 seconds of your video file and automatically calculates the silence threshold, the 
file location, which you can use the 'Browse' button to navigate through your own file navigation
system to locate your video file, and a button to delete extracted clips, which is false by default
meaning you will keep the extracted non-silence clips. 

The GUI also has a progress bar indicating the progress of iterating over your audio from your
video file.

The output is a video file that has been clipped together of all the non-silence clips,
including a BUFFER time jacket.

Note: It is recommended to run this in a folder, so that you can have all the contents
(tmp folder, output_video.mp4) in the same place

=== Future Development ===

- Cancel Button: To do so would require multiprocessing/threading, which
I did not find an easy way to implement while importing the video editing script into
the video editor GUI

- Speech Recognition
