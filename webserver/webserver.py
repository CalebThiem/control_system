# Define a function that sends output states to the Arduino

first_leaching_pin = 1

last_leaching_pin = 32

current_pin_states = []

for i in range(300):

    current_pin_states.append("0")

temp = 1

for i in range(last_leaching_pin, 48 + 1):

    current_pin_states[i] = temp

    temp += 1


def update_leaching_pins(current_pin_states, active_pins, first_leaching_pin, last_leaching_pin):

    current_pin_states_copy = current_pin_states

    for pin in range(first_leaching_pin,last_leaching_pin + 1):

        current_pin_states_copy[pin - 1] = "0"
    
    for pin in active_pins:

        current_pin_states_copy[pin - 1] = pin

    return current_pin_states_copy


temp = 1

active_pins = []


for i in range(first_leaching_pin - 1, last_leaching_pin):

    active_pins.append(temp)

    temp += 1

current_pin_states = update_leaching_pins(current_pin_states, active_pins, first_leaching_pin, last_leaching_pin)


print(current_pin_states)


# Define a function that gets sensor data from the Arduino

