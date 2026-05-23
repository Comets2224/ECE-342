import serial
import numpy as np
import time
import pyqtgraph
import tkinter as tk
import threading

RETURN_CODES = {
    b'\x00':"OK",
    b'\x01':"Waveform file of this name already exists.",
    b'\x02':"Could not connect to thumbdrive."
}

#Sampling constants
NUM_SAMPLES = 1250 #The number of samples in a single frame of a wave
TOTAL_BYTES = NUM_SAMPLES * 4 #Each sample from the Teensy contains a sample of each channel.  
FACTOR = 3.3 / ((2**10) - 1) #FACTOR RIGHT NOW IS SET UP FOR 0V TO 3.3V SIGNALS!!!!!

#GUI constants
BACKGROUND_COLOR = "lightgray"
SECTION_PADDING = 25
ELEMENT_PADDING = 25
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_SIDE_PADDING = 400 - (2 * BUTTON_WIDTH) / 3
VALID_CHARACTERS = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "."};

stop_flag = 1 #When set, the script will not query the microcontroller for samples. #When not set, python script will indefinitely request samples.
terminate_flag = 0 #Signals that the UI has been closed by the user and that the main thread must join all other threads and terminate.
save_zero_flag = 0
save_one_flag = 0
return_recv_flag = 0
latest_return_code = None
output_buffer = None

trigger_buffer0 = None
trigger_buffer1 = None

trigger_setting = 0
trigger_type = "RE"

total_bytes_read = 0
wave0 = None #The array that holds one frame of data from channel 0. Size of NUM_SAMPLES constant.
wave1 = None #The array that holds one frame of data from channel 1. Size of NUM_SAMPLES constant.

serial_obj = None

def receive_samples():
    """Receive samples from the Teensy until the stop_flag is set to 1. Samples are split by channel and are
        accessible using the wave0 and wave1 arrays."""

    #Use the global keyword to tell python that these variables are the same as the variables outside the function.
    global total_bytes_read
    global wave0
    global wave1

    #Debug stuff
    total_bytes_read = 0
    start = time.perf_counter()
    end = time.perf_counter()

    while not stop_flag:

        #Send command 0x01 (START) to the microcontroller, the microcontroller will send NUM_SAMPLES samples of each waveform in return.
        serial_obj.reset_input_buffer()
        serial_obj.write(b'\x01')
        serial_obj.flush()

        #Read the waveform data. The data of each waveform are currently intertwined.
        raw = serial_obj.read(TOTAL_BYTES)
        total_bytes_read += len(raw)

        #Decode the data into numbers. Untie the waveforms from each other into wave0 and wave1 arrays, each of size NUM_SAMPLES
        samples = np.frombuffer(raw, dtype='<u2')
        wave0 = samples[0::2] * FACTOR
        wave1 = samples[1::2] * FACTOR

        #More debug stuff
        end = time.perf_counter()
        print(f"{total_bytes_read} bytes ({total_bytes_read / 4} samples) read and converted in {end - start:.6f} s")
        #graph.setData(wave0)

    #More debug stuff
    print(f"\n[SAMPLING STOPPED] {total_bytes_read} bytes ({total_bytes_read / 4} samples) read in {end - start:.6f} s")
    print(f"Per-Channel Sampling Frequency: ~{(total_bytes_read / 4) / (end - start):.0f} Hz")

def wait_for_response():
    """Called after a command is sent to the microcontroller to catch the microcontroller's response."""
    global RETURN_CODES
    global latest_return_code
    global return_recv_flag
    #Read the one byte return code.
    latest_return_code = serial_obj.read(1)
    return_recv_flag = 1
    #Print the code and its corresponding text to the terminal
    print(f"[UC RESPONSE] T4.1 returns {latest_return_code}: '{RETURN_CODES[latest_return_code]}'")

def ui_operations():
    """All of the code that controls the UI goes here. This code is run in a parallel thread to the main thread."""

    #Create the window.
    gui_window = tk.Tk()
    gui_window.title("KGH Oscilloscope Control Software")
    gui_window.geometry("400x1080")
    gui_window.resizable(False, False)
    gui_window.config(bg = BACKGROUND_COLOR)

    #Header at the top of the window
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

    #"Start sampling" button
    start_button = tk.Button(
        text = "Start Sampling",
        font = ("Arial"),
    )
    start_button.place(x = 33, y = 125, width = 150, height = 50)

    #"Stop sampling" button.
    stop_button = tk.Button(
        text = "Stop Sampling",
        font = ("Arial"),
    )
    stop_button.place(x = 216, y = 125, width = 150, height = 50)

    #Saving controls section

    saving_header_label = tk.Label(
        text = "⎯⎯⎯⎯⎯⎯ Saving Controls ⎯⎯⎯⎯⎯⎯",
        font = ("Arial", 15, "bold"),
        bg = BACKGROUND_COLOR
    )
    saving_header_label.place(x = 0, y = 200 , width = 400, height = 25)

    #Textbox to enter a filename.
    filename_entry = tk.Entry(
        text = "Filename",
        font = ("Arial", 15)
    )
    filename_entry.place(x = 33, y = 250, width = 333, height = 50)

    #"Save waveform 0" button.
    save0_button = tk.Button(
        text = "Save Wave 0",
        font = ("Arial"),
    )
    save0_button.place(x = 33, y = 325, width = 150, height = 50)

    #"Save waveform 1" button.
    save1_button = tk.Button(
        text = "Save Wave 1",
        font = ("Arial"),
    )
    save1_button.place(x = 216, y = 325, width = 150, height = 50)

    #Trigger controls section

    saving_header_label = tk.Label(
        text = "⎯⎯⎯⎯⎯⎯ Trigger Controls ⎯⎯⎯⎯⎯⎯",
        font = ("Arial", 15, "bold"),
        bg = BACKGROUND_COLOR
    )
    saving_header_label.place(x = 0, y = 400 , width = 400, height = 25)

    #"Enter a new trigger value" textbox.
    trig_entry = tk.Entry(
        text = "Trigger Value",
        font = ("Arial", 15)
    )
    trig_entry.place(x = 33, y = 450, width = 150, height = 50)

    #"Set desired trigger value" button.
    apply_trig_button = tk.Button(
        text = "Apply",
        font = ("Arial"),
    )
    apply_trig_button.place(x = 216, y = 450, width = 150, height = 50)

    # Error window section
    # Frame that displays an error message if one exists.
    info_ribbon = tk.Label(
        text = "test",
        font = ("Arial"),
        bg = "red",
        fg = "white"
    )

    #"Acknowledge error" button.
    ack_button = tk.Button(
        text = "OK",
        font = ("Arial")
    )

    def set_info_ribbon(is_success, return_text):
        """Display the given return message (return_text)"""

        # start_button_state = start_button.cget("state")
        # stop_button_state = stop_button.cget("state")
        # save0_button_state = save0_button.cget("state")
        # save1_button_state = save1_button.cget("state")

        # start_button.config(state = "disabled")
        # stop_button.config(state = "disabled")
        # save0_button.config(state = "disabled")
        # save1_button.config(state = "disabled")

        if is_success:
            info_ribbon.config(background = "green")
        else:
            info_ribbon.config(background = "red")

        info_ribbon.config(text = return_text)
        info_ribbon.place(x = 0, y = 600 , width = 400, height = 100)
        ack_button.place(x = 216, y = 725, width = 150, height = 50)

    def clear_info_ribbon():
        """Hide the info frame"""
        info_ribbon.place_forget()
        ack_button.place_forget()
    #Set ack_button to trigger clear_info_ribbon when clicked
    ack_button.config(command = clear_info_ribbon)

    def test_print():
        print("This button is not yet functional.")

    def start_pressed():
        """Allow the main thread to start receiving samples from the microcontroller by turning off the stop_flag."""
        start_button.config(state = "disabled")
        stop_button.config(state = "normal")
        save0_button.config(state = "disabled")
        save1_button.config(state = "disabled")
        print("Sending 0x01 (START)")
        global stop_flag 
        stop_flag = 0

    start_button.config(command = start_pressed)

    def stop_pressed():
        """Stop the main thread from receiving samples from the microcontroller by setting the stop_flag."""
        start_button.config(state = "normal")
        stop_button.config(state = "disabled")
        save0_button.config(state = "normal")
        save1_button.config(state = "normal")
        print("Sending 0x02 (STOP)")
        global stop_flag
        stop_flag = 1

    stop_button.config(state = "disabled", command = stop_pressed)

    def process_save_request(channel_to_save):
        """Tell the main thread to tell the microcontroller to save a specified waveform to the thumbdrive."""
        #Disable all buttons
        start_button.config(state = "disabled")
        stop_button.config(state = "disabled")
        save0_button.config(state = "disabled")
        save1_button.config(state = "disabled")

        #Get the text entered in the file name field.
        user_provided_filename = filename_entry.get()
        #Check if the user hasn't entered a file name.
        if user_provided_filename == "":
            return_text = "Enter a file name for the file you want to create."
            print(return_text)
            set_info_ribbon(0, return_text)
        #Check if the user entered a file name which is too long.
        elif len(user_provided_filename) > 49:
            return_text = "File names can be no longer than 50 characters."
            print(return_text)
            set_info_ribbon(0, return_text)
        else:
            global RETURN_CODES
            global output_buffer
            global latest_return_code
            global return_recv_flag
            global save_zero_flag
            global save_one_flag

            if channel_to_save == 0:
                print("Sending 0x03 (OFFLOAD WAVE 0)")
            else:
                print("Sending 0x04 (OFFLOAD WAVE 1)")

            #Load the output buffer with the ASCII-encoded file name so that the main thread can send it to the microcontroller.
            output_buffer = user_provided_filename.encode('ASCII')

            #Set the corresponding save flag for which channel is to be saved so the main thread can perform the relevant task.
            if channel_to_save == 0:
                save_zero_flag = 1
            else:
                save_one_flag = 1

            #Wait for the return received flag to be set.
            while not return_recv_flag:
                continue

            return_recv_flag = 0
            
            #Read the return code, display an error if the return is anything other than 0x00 (OK)
            if latest_return_code != b'\x00':
                print(RETURN_CODES[latest_return_code])
                set_info_ribbon(0, RETURN_CODES[latest_return_code])
            else: 
                set_info_ribbon(1, f"Waveform {channel_to_save} was written succesfully.")

        #Enable buttons.
        start_button.config(state = "normal")
        stop_button.config(state = "disabled")
        save0_button.config(state = "normal")
        save1_button.config(state = "normal")

    def savew0_pressed():
        """Run the process save function with the argument of 0 to save waveform 0."""
        process_save_request(0)

    save0_button.config(state = "disabled", command = savew0_pressed)

    def savew1_pressed():
        """"Run the process save function with the argument of 1 to save waveform 1."""
        process_save_request(1)

    save1_button.config(state = "disabled", command = savew1_pressed)

    def validate_trig_entry(user_trigger_setting):
        """Checks that an entry to the trigger setting entry box is within +/-16.5 and doesn't have non-numeric characters"""

        if user_trigger_setting == "":
            return 0

        #Check for non-numeric characters
        for char in user_trigger_setting:
            if not char in VALID_CHARACTERS:
                return 0

        converted_trig_val = float(user_trigger_setting)

        #Check that the float value is actually in-bounds.
        if converted_trig_val > 16.5 or converted_trig_val < -16.5:
            return 0   
        
        return 1

    def apply_pressed():
        """Update the global variable for trigger setting to a new user-defined input."""
        user_trigger_setting = trig_entry.get()
        if validate_trig_entry(user_trigger_setting) == 1:
            global trigger_setting
            trigger_setting = user_trigger_setting
            print(f"[INFO] Trigger value is now {trigger_setting}")
            set_info_ribbon(1, "Trigger updated")
        else:
            return_text = "Invalid input (Numbers between +/-16.5 only)."
            set_info_ribbon(0, return_text)

    apply_trig_button.config(command = apply_pressed)

    #Run the mainloop, which is an infinite loop that detects inputs and handles them
    gui_window.mainloop()

    #When the program reaches this point, the GUI window was closed, set the stop and terminate flags so other threads
    #   know to stop what they are doing and terminate cleanly. The mainthread handles final cleanup later.
    global stop_flag
    stop_flag = 1

    global terminate_flag
    terminate_flag = 1

def display_operations():
    """All of the code that controls the display goes here. This code is run in a parallel thread to the main thread."""
    # global trigger_buffer0
    # global trigger_buffer1
    # global wave0
    # global wave1
    # trigger_buffer0 = np.copy(wave0)
    # trigger_buffer1 = np.copy(wave1)

    def find_trigger_point():
        """Finds and returns the index of the first data point that meets the trigger requirements."""
        global trigger_value
        global trigger_type
        global wave0
        if trigger_type == "RE":
            for j in range(1, NUM_SAMPLES):
                if wave0[j - 1] < trigger_value and wave0[j] >= trigger_value:
                    return j
        elif trigger_type == "FE":
            for j in range(1, NUM_SAMPLES):
                if wave0[j - 1] >= trigger_value and wave0[j] < trigger_value:
                    return j
        elif trigger_type == "FIRST":
            for j in range(NUM_SAMPLES):
                if wave0[j] >= trigger_value:
                    return j

    #TODO 4 hunter, display code here

def main_thread_loop():
    """This is the loop for the main thread. The main thread handles reading waveform data from the Teensy."""
    global save_zero_flag
    global save_one_flag
    global stop_flag
    global terminate_flag

    while True:
        if not stop_flag:
            receive_samples()
        else:
            if terminate_flag:
                break
            elif save_zero_flag:
                save_zero_flag = 0
                serial_obj.reset_input_buffer()
                serial_obj.write(b'\x03')
                serial_obj.write(output_buffer)
                serial_obj.flush()
                wait_for_response()

            elif save_one_flag:
                save_one_flag = 0
                serial_obj.reset_input_buffer()
                serial_obj.write(b'\x04')
                serial_obj.write(output_buffer)
                serial_obj.flush()
                wait_for_response()
                

#Main thread execution:

#Create the UI Thread and Display Thread
ui_thread = threading.Thread(target = ui_operations)
display_thread = threading.Thread(target = display_operations)

#Open communication with Teensy
serial_obj = serial.Serial('COM7', 6000000, timeout=10)

#Start up all threads.
print(f"\n=====  Connected to: {serial_obj.name} at {serial_obj.baudrate} baud  =====\n")
ui_thread.start()
display_thread.start()
main_thread_loop()

#Close the UI and Display threads
ui_thread.join()
display_thread.join()

#Close communication with Teensy
serial_obj.close()

# print(f"\nTest graph is generating...")
# graph = pyqtgraph.plot(y=wave0, pen='y')
# graph.plot(y=wave1, pen='c')

# pyqtgraph.exec()
