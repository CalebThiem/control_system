import time

from arduino import Arduino

arduino = Arduino()

print("Initiating serial connection on /dev/ttyACM1")

while arduino.connect('/dev/ttyACM1', 460800) == 'connection_failed':

    print("Connection failed. Retrying...")

    time.sleep(1)

print("Established connection")

print("Waiting for Arduino to reset...")

print("Receiving input pin state data from Arduino...")

time.sleep(2)

while True:

    arduino.serial_communicate("?")

    print(arduino.receive_data())

    time.sleep(0.1)

