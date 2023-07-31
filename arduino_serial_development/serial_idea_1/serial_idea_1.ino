import serial
import time
import random

ser = serial.Serial('/dev/ttyACM0', 115200)  # replace '/dev/ttyACM0' with your serial port

# Wait for the Arduino to reset
time.sleep(2)

successes = 0
failures = 0

for _ in range(1000):
    data = ''.join(random.choice('01') for _ in range(150))  # Generate random data

    # Send the data
    ser.write(b'a')
    for char in data:
        ser.write(char.encode())
        time.sleep(0.00001)  # Delay to prevent Arduino's serial buffer from overflowing
    ser.write(b'z')

    # Print out the sent data
    print('Sent data:    ', data)

    time.sleep(0.05)

    # Wait for the Arduino to send back the data
    received_data = ser.readline().decode().strip()

    # Verify the data
    if received_data == data:
        successes += 1
    else:
        failures += 1
        print('Error: Data verification failed')

    # Print out debug info from the Arduino
    while ser.in_waiting > 0:
        print(ser.readline().decode().strip())

print('Successes:', successes)
print('Failures:', failures)

ser.close()