from arduino import Arduino
from pin_handler import PinHandler
from SPV_control import SpvControl


arduino = Arduino()

arduino.connect('/dev/ttyACM0', 9000)

pinHandler = PinHandler()
spv = SpvControl(pinHandler, arduino)
