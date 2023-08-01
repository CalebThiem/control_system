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

data = "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"

print(calculate_checksum(data))