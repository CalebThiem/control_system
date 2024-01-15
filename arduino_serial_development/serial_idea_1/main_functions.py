
def on_close():

    global arduino
    global shutdown 
    global root
    
    if arduino.connection_ready:
    
        arduino.disconnect()

        root.after_cancel(refresh_arduino_input_data_sheduled)

    steps.cancel()

    root.destroy()

def previous_button_press():

    steps.load_previous_step()

def next_button_press():

    steps.load_next_step()

def start_button_press():

    # Grey out buttons

    next_button.config(state=tk.DISABLED)

    previous_button.config(state=tk.DISABLED)

    start_button.config(state=tk.DISABLED)

    steps.call_current_thread()

    steps.start_button_pressed = True
    
    steps.stop_button_pressed = False

def stop_button_press():

    steps.cancel()

    steps.start_button_pressed = False

    steps.stop_button_pressed = True

    next_button.config(state=tk.NORMAL)

    previous_button.config(state=tk.NORMAL)

    start_button.config(state=tk.NORMAL)


def refresh_arduino_input_data():
    
    global root
    global arduino
    global arduino_input_data
    global input_data_display
    global shutdown
    global refresh_arduino_input_data_sheduled

    if (arduino.connection_ready):

        arduino_input_data = arduino.read_inputs()

    else:

        arduino_input_data = ['no_connection']

    input_data_display.update_gui(arduino_input_data)

    refresh_arduino_input_data_sheduled = root.after(200, refresh_arduino_input_data)

def count_input_data_elements():

    global arduino

    global arduino_input_data

    if (arduino.connection_ready):

        arduino_input_data = arduino.read_inputs()

        element_count = len(arduino_input_data)

        return element_count

def popup_manager():

    global arduino
    global popup
    global popup_text

    if arduino.connection_ready:

        popup.destroy()

    else:

        popup_text.config(text="Arduino connection failed. Check connection and restart program")

def arduino_tasks():

    global arduino
    global input_data_display

    if arduino.connection_ready:
        
        input_data_display = Gui(frame_right, number_of_labels=count_input_data_elements(), pady=0)

        refresh_arduino_input_data()


