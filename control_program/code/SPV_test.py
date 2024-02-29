from arduino import Arduino
from pin_handler import PinHandler
from SPV_control import SpvControl

def process_string(input_string):
    # Split the string by hyphens
    parts = input_string.split('-')

    # Process the first part (series of '1's) into individual digits
    first_part_digits = list(parts[0])

    # Combine the individual digits with the remaining parts
    processed_list = first_part_digits + parts[1:]

    return processed_list

arduino = Arduino()

arduino.connect('/dev/ttyACM0', 9000)

pin_handler = PinHandler()

spv = SpvControl(pin_handler, arduino)


