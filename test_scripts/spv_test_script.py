from arduino import Arduino
from SPV_control import SpvControl
from pin_handler import PinHandler

arduino = Arduino()
pin_handler = PinHandler()
spv = SpvControl(pin_handler, arduino)

arduino.connect('/dev/ttyACM0', 480600)

print("SPV methods:")
print("start_rotation")
print("stop_rotation")
print("rotate_clockwise")
print("rotate_anticlockwise")
print("start_inflation_cycle")
print("disable_inflation_cycle")
print("start_evacuation_sequence")



