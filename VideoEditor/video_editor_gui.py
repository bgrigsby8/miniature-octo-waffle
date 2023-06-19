#!/usr/bin/python3

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import video_editor

curr_directory = os.getcwd()
process_output_success = "The edited video can be found at {}/output_video.mp4".format(curr_directory)
process_output_failure = "There was an error. Contact Brad. "
TIME_LABEL_TEXT = "Duration of silence in between non-silence to be cut out from video (seconds) [default: 2])"
THRESHOLD_LABEL_TEXT = "Manually adjust silence threshold, which determines minimum sound level to be considered silence [default: 1500])"
OUTPUT_FILE_LOCATION_TEXT = "Use 'Browse' to navigate through your file navigation system (location of video file [default: None])"
DYNAMIC_THRESHOLD_DESCRIPTION = "Enabling 'Dynamically Adjust Threshold' wll automatically determine the appropriate silence threshold. To use this, leave 3 seconds of silence at the beginning of the video. That will be used to calculate the silence threshold."

def browse_file():
    filepath = filedialog.askopenfilename(initialdir=curr_directory, title="Select Video File",
                                          filetypes=(("MP4 files", "*.mp4"), ("all files", "*.*")))
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(tk.END, filepath)

def cancel_script():
    if messagebox.askyesno("Confirmation", "Are you sure you want to cancel the script?"):
        cancel_flag[0] = True

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
    if not threshold_value and threshold_checkbox.get() == 0:
        threshold_value = 1500
    elif not threshold_value:
        threshold_value = 0

    delete_tmp = delete_tmp_checkbox.get()

    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    try:
        video_editor.main(int(time_value), int(threshold_value), filepath, delete_tmp, progress_callback=update_progress)
        messagebox.showinfo("Brad just did all your work. Pay him", process_output_success)
    except Exception as e:
        messagebox.showinfo("Brad fucked up", process_output_failure + "Error: {}".format(e))

def toggle_threshold_adjustment():
    if threshold_entry.get():
        threshold_entry.config(state=tk.DISABLED)
    else:
        threshold_entry.config(state=tk.NORMAL)

    if threshold_checkbox.get() == 0:
        threshold_entry.config(state=tk.NORMAL)
    else:
        threshold_entry.delete(0, tk.END)
        threshold_entry.config(state=tk.DISABLED)


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
description_font = ("Arial", 10)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

desired_screen_width = int(screen_width * 0.6)
desired_screen_height = int(screen_height * 0.65)

window.geometry(f"{desired_screen_width}x{desired_screen_height}")

window.update_idletasks()  # Ensure window dimensions are updated
x_offset = (screen_width - window.winfo_width()) // 2
y_offset = (screen_height - window.winfo_height()) // 2
window.geometry(f"+{x_offset}+{y_offset}")

style = ttk.Style()
style.configure("TLabel", background="white", font=label_font)
style.configure("TButton", font=button_font)
style.configure("TCheckbutton", font=label_font, background="white")
style.configure("DescriptionLabel.TLabel", font=description_font)

# Create labels and entry fields for inputs
time_label = ttk.Label(window, text="Time:", wraplength=500)
time_label.pack(pady=(30, 0))
time_entry = ttk.Entry(window, width=40)
time_entry.pack(pady=(5, 0))
time_label_description = ttk.Label(window, text=TIME_LABEL_TEXT, wraplength=900, style="DescriptionLabel.TLabel")
time_label_description.pack(pady=(0,0))

threshold_label = ttk.Label(window, text="Silence Threshold:", wraplength=500)
threshold_label.pack(pady=(30, 0))
threshold_entry = ttk.Entry(window, width=40)
threshold_entry.pack(pady=(5, 0))
threshold_label_description = ttk.Label(window, text=THRESHOLD_LABEL_TEXT, wraplength=900, style="DescriptionLabel.TLabel")
threshold_label_description.pack(pady=(0,0))

threshold_checkbox = tk.IntVar()
threshold_checkbox.set(0)
threshold_adjustment_checkbox = ttk.Checkbutton(window,
                                                text="Dynamically Adjust Threshold",
                                                variable=threshold_checkbox,
                                                command=toggle_threshold_adjustment,
                                                state=tk.NORMAL
                                                )
threshold_adjustment_checkbox.pack(pady=(5, 0))

dynamic_threshold_description = ttk.Label(window, text=DYNAMIC_THRESHOLD_DESCRIPTION, wraplength=900, style="DescriptionLabel.TLabel")
dynamic_threshold_description.pack(pady=(0,0))

browse_file_label = ttk.Label(window, text="File location:", wraplength=500)
browse_file_label.pack(pady=(30, 0))

label_var = tk.StringVar()
label_var.trace("w", check_label_content)
file_entry = ttk.Entry(window, textvariable=label_var, width=40)
file_entry.pack(pady=(5, 0))
file_entry.config(font=button_font)

browse_file_description = ttk.Label(window, text=OUTPUT_FILE_LOCATION_TEXT, wraplength=900, style="DescriptionLabel.TLabel")
browse_file_description.pack(pady=(0,0))

# Create a button to browse for a file
browse_button = ttk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=(5, 0))

delete_tmp_checkbox = tk.IntVar()
delete_tmp_checkbox.set(0)
delete_tmp_adjustment_checkbox = ttk.Checkbutton(window,
                                                 text="Delete extracted clips [default: false]",
                                                 variable=delete_tmp_checkbox,
                                                 )
delete_tmp_adjustment_checkbox.pack(pady=(5,0))

progress_label = ttk.Label(window, text="Progress Bar")
progress_label.pack(pady=(50, 0))
progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
progress_bar.pack(pady=10)

# Create a button to run the script
start_button = ttk.Button(window, text="Start", command=run_video_editor, state=tk.DISABLED)
start_button.pack(pady=30)

# TODO: Implement Cancel button
# cancel_button = ttk.Button(window, text="Cancel", command=cancel_script, state=tk.DISABLED)
# cancel_button.pack(side=tk.RIGHT)

# Start the GUI event loop
window.mainloop()
