from arduino import Arduino
from pin_handler import PinHandler
from SPV_control import SPV_control

arduino = Arduino()
pinHandler = PinHandler()
spv = SPV_control(pinHandler, arduino)

arduino.connect('/dev/ttyACM0', 9000)
