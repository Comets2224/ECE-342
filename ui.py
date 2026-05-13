#import serial
#import numpy as np
#import time
#import pyqtgraph
import tkinter as tk
import threading

BACKGROUND_COLOR = "lightgray"
SECTION_PADDING = 25
ELEMENT_PADDING = 25
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_SIDE_PADDING = 400 - (2 * BUTTON_WIDTH) / 3

def test_print():
    print("Button pressed.")

def ui_operations():

    gui_window = tk.Tk()
    gui_window.title("KGH Oscilloscope Control Software")
    gui_window.geometry("400x1080")
    gui_window.resizable(False, False)
    gui_window.config(bg = BACKGROUND_COLOR)

    name_label = tk.Label(
        text = "KGH Oscilloscope Control",
        font = ("Arial", 25),
        fg = "white",
        bg = "gray",
    )
    name_label.place(x = 0, y = 0, width = 400, height = 50)

    #Sampling controls section

    sampling_header_label = tk.Label(
        text = "⎯⎯⎯⎯⎯⎯ Sampling Controls ⎯⎯⎯⎯⎯⎯",
        font = ("Arial", 15, "bold"),
        bg = BACKGROUND_COLOR
    )
    sampling_header_label.place(x = 0, y = 75 , width = 400, height = 25)

    start_button = tk.Button(
        text = "Start Sampling",
        font = ("Arial"),
        command = test_print
    )
    start_button.place(x = 33, y = 125, width = 150, height = 50)

    stop_button = tk.Button(
        text = "Stop Sampling",
        font = ("Arial"),
        command = test_print
    )
    stop_button.place(x = 216, y = 125, width = 150, height = 50)

    #Saving controls section

    saving_header_label = tk.Label(
        text = "⎯⎯⎯⎯⎯⎯ Saving Controls ⎯⎯⎯⎯⎯⎯",
        font = ("Arial", 15, "bold"),
        bg = BACKGROUND_COLOR
    )
    saving_header_label.place(x = 0, y = 200 , width = 400, height = 25)

    save0_button = tk.Button(
        text = "Save Wave 0",
        font = ("Arial"),
        command = test_print
    )
    save0_button.place(x = 33, y = 250, width = 150, height = 50)

    save1_button = tk.Button(
        text = "Save Wave 1",
        font = ("Arial"),
        command = test_print
    )
    save1_button.place(x = 216, y = 250, width = 150, height = 50)

    #Trigger controls section

    saving_header_label = tk.Label(
        text = "⎯⎯⎯⎯⎯⎯ Trigger Controls ⎯⎯⎯⎯⎯⎯",
        font = ("Arial", 15, "bold"),
        bg = BACKGROUND_COLOR
    )
    saving_header_label.place(x = 0, y = 325 , width = 400, height = 25)

    trig_entry = tk.Entry(
        text = "Trigger Value",
        font = ("Arial", 15)
    )
    trig_entry.place(x = 33, y = 375, width = 150, height = 50)

    apply_trig_button = tk.Button(
        text = "Apply",
        font = ("Arial"),
        command = test_print
    )
    apply_trig_button.place(x = 216, y = 375, width = 150, height = 50)

    gui_window.mainloop()

ui_thread = threading.Thread(target = ui_operations)
ui_thread.start()
ui_thread.join()
