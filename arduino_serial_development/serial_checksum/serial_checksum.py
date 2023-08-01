import serial
import time
import random

data = "1" *150  # replace with your data

def calculate_checksum(data):

    crc = 0
    for i in range(len(data)):
        crc ^= ord(data[i])
        for j in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF  # Ensure byte size in Python 3
        # print("Intermediate checksum: ", hex(crc))
    return crc


def send_to_Arduino(data):

    # Calculate the checksum
    checksum = calculate_checksum(data)

    # Send the data and the checksum
    ser.write(b'a')
    for char in data:
        ser.write(char.encode())
        time.sleep(0.0001)  # Delay to prevent Arduino's serial buffer from overflowing
    ser.write(format(checksum, '02X').encode())
    ser.write(b'z')

    # Print out the sent data and checksum
    # print('Sent pinArray:', data)
    # print('Sent checksum:', format(checksum, '02X'))

    time.sleep(0.05)

    # Wait for the Arduino to send back the data
    result = ser.readline().decode().strip()

    # print('Received pinArray:', pinArray)


    # Verify the data
    if result == "valid":
        return(1)
    else:
        return(0)

    # Print out debug info from the Arduino
    # while ser.in_waiting > 0:
    #    print(ser.readline().decode().strip())

successes = 0
errors = 0



for i in range(10):

    ser = serial.Serial('/dev/ttyACM0', 115200)  # replace '/dev/ttyACM0' with your serial port

    # Wait for the Arduino to reset

    time.sleep(2)


    data = ''.join(random.choice('01') for _ in range(150))
    # print(data)
    if send_to_Arduino(data) == 1:
        successes += 1
    else:
        errors += 1

ser.close()

print("Successes: ", successes)
print("Errors", errors)



