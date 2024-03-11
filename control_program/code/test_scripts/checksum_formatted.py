import binascii

def add_checksum(data):

    # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string

    checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

    # Return the checksum followed by the original data

    checksum = checksum.upper()

    return checksum + data

def build_string(number_of_relays):

    output = []

    for i in range(number_of_relays):

        output.append("1")

    for i in range(96 - number_of_relays):

        output.append("0")

    return output

data = input()

output = "<%s>" % add_checksum("".join(build_string(int(data))))

print(output)

