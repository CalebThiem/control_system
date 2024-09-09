from machine import UART
import sys

# Initialize UART0 with a baud rate of 9600
uart = UART(0, baudrate=9600)

while True:
    if uart.any():  # Check if any data is available on UART0
        data = uart.read()  # Read the data from UART0
        if data:
            sys.stdout.write(data.decode('utf-8'))  # Print the received data to the terminal

