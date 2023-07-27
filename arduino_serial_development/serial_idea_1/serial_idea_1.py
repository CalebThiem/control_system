import serial
import time

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)

high = [1]

low = [0]

high.append(13)

high_len = len(high)

low.append(13)

low_len = len(low)

arduino.write(high, high_len)

print("Transmit: ", high)

time.sleep(1)

check = arduino.readline()

print(check)

