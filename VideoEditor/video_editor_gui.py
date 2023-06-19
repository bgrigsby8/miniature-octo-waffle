#!/usr/bin/python3

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import time
import video_editor

curr_directory = os.getcwd()
process_output_success = "The edited video can be found at {}/output_video.mp4".format(curr_directory)
process_output_failure = "There was an error. Contact Brad"
TIME_LABEL_TEXT = "Time (duration of silence in between non-silence to be cut out from video (seconds) [default: 2]):"
THRESHOLD_LABEL_TEXT = "Threshold (manually adjust silence threshold, which determines minimum sound level to be considered silence [default: 1500]):"
OUTPUT_FILE_LOCATION_TEXT = "File location, use 'Browse' to navigate through your file navigation system (location of video file [default: None])"

def browse_file():
    filepath = filedialog.askopenfilename(initialdir=curr_directory, title="Select Video File",
                                          filetypes=(("MP4 files", "*.mp4"), ("all files", "*.*")))
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(tk.END, filepath)


def update_progress(progress):
    progress_bar["value"] = progress
    window.update_idletasks()


def run_video_editor():
    filepath = file_entry.get()
    if not filepath:
        messagebox.showwarning("Error", "Please select a video file.")
        return

    time_value = time_entry.get()
    if not time_value:
        time_value = 2

    threshold_value = threshold_entry.get()
    if not threshold_value:
        threshold_value = 1500

    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    # Call the video_editor.main function with the progress callback
    video_editor.main(int(time_value), int(threshold_value), filepath, progress_callback=update_progress)

    messagebox.showinfo("Video Editor", "Video editing complete.")


def check_label_content(*args):
    if file_entry.get():
        start_button.config(state=tk.NORMAL)
    else:
        start_button.config(state=tk.DISABLED)


window = tk.Tk()
window.title("Brad's Video Editor")
window.configure(bg="white")
label_font = ("Arial", 12)
button_font = ("Arial", 12)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

desired_screen_width = int(screen_width * 0.6)
desired_screen_height = int(screen_height * 0.6)

window.geometry(f"{desired_screen_width}x{desired_screen_height}")

window.update_idletasks()  # Ensure window dimensions are updated
x_offset = (screen_width - window.winfo_width()) // 2
y_offset = (screen_height - window.winfo_height()) // 2
window.geometry(f"+{x_offset}+{y_offset}")

style = ttk.Style()
style.configure("TLabel", background="white", font=label_font)
style.configure("TButton", font=button_font)

# Create labels and entry fields for inputs
time_label = ttk.Label(window, text=TIME_LABEL_TEXT)
time_label.pack(pady=(30, 0))
time_entry = ttk.Entry(window, width=40)
time_entry.pack(pady=(5, 0))

threshold_label = ttk.Label(window, text=THRESHOLD_LABEL_TEXT)
threshold_label.pack(pady=(30, 0))
threshold_entry = ttk.Entry(window, width=40)
threshold_entry.pack(pady=(5, 0))

browse_file_label = ttk.Label(window, text=OUTPUT_FILE_LOCATION_TEXT)
browse_file_label.pack(pady=(30, 0))

label_var = tk.StringVar()
label_var.trace("w", check_label_content)
file_entry = ttk.Entry(window, textvariable=label_var, width=40)
file_entry.pack(pady=(5, 0))
file_entry.config(font=button_font)

# Create a button to browse for a file
browse_button = ttk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=(5, 0))

progress_label = ttk.Label(window, text="Progress Bar")
progress_label.pack(pady=(50, 0))
progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
progress_bar.pack(pady=10)

# Create a button to run the script
start_button = ttk.Button(window, text="Start", command=run_video_editor, state=tk.DISABLED)
start_button.pack(pady=30)

# Start the GUI event loop
window.mainloop()
