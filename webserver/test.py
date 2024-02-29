from nicegui import ui, app

import threading 

import sys

import time

loop = True

with ui.splitter() as splitter:

    with splitter.before:

        label_1 = ui.label().classes('mr-2')

    with splitter.after:

        label_2 = ui.label().classes('ml-2')


def leaching_step_1():

    global label_1

    global loop

    label_1.set_text("Leaching Step 1")

    next_step = threading.Timer(2.0, leaching_step_2)

    if loop == True:
    
        next_step.start()


def leaching_step_2():

    global label_1

    global loop

    label_1.set_text("Leaching Step 2")

    next_step = threading.Timer(2.0, leaching_step_1)

    if loop == True:

        next_step.start()

def electrowinning_step_1():

    global label_2

    global loop

    label_2.set_text("Electrowinning Step 1")

    next_step = threading.Timer(1.0, electrowinning_step_2)

    if loop == True:

        next_step.start()


def electrowinning_step_2():

    global label_2

    global loop

    label_2.set_text("Electrowinning Step 2")

    next_step = threading.Timer(1.0, electrowinning_step_1)

    if loop == True:

        next_step.start()

def end_Loop():

    global loop

    loop = False

    time.sleep(2)

    app.shutdown()
    
    sys.exit()

ui.run(native = True, reload = False)

end_loop_timer = threading.Timer(10.0, end_Loop)

end_loop_timer.start()

leaching_step_1()   

electrowinning_step_1()

