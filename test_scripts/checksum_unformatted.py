import binascii


def add_checksum(data):

    # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string

    checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

    # Return the checksum followed by the original data

    checksum = checksum.upper()

    return checksum + data


data = input()

output = "<%s>" % add_checksum(data)

print(output)

