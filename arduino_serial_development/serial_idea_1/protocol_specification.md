## Description ##

Communicates with an Arduino over serial, sending and receiving strings up to 300 characters in length. 

Advantages: easy to understand and modify

Disadvantages: inefficient

## General Behaviour ##

# Baud Rate #

Arduino opens serial port at 460800 baud.

# Serial Transmission #

Message is up to 300 bytes long. Each byte represents an ASCII text character.

The first byte is a '<'. This signifies the start of the message. 

The next 8 bytes comprise a zero-padded, capitalised hexadecimal CRC32 checksum of the rest of the message, excluding the last character.

The last byte is a '>'. This signifies the end of the message.

Upon receiving a properly formatted message, the Arduino will respond with one of the following transmissions:

    "Verified" is sent if the checksum matches the computed checksum

    "ChecksumFailed" is sent if the checksum does not match the computed checksum

    If the first character after the checksum was a '?', the Arduino will then send a message of its own, with identical formatting.

