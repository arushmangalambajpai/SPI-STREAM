"""
SPI Header Decoder

Responsible for decoding TPM SPI transaction layer.

This file converts raw SPI bytes into a stream array.

It extracts:

1. Operation Header
2. READ / WRITE operation
3. Transfer byte length
4. TPM locality
5. Register address
6. Register payload


It does NOT decode:

- FIFO registers
- CRB registers
- TPM commands
"""


# ==========================================================
# HEX STRING CONVERSION
# ==========================================================


def hex_string_to_list(hex_string):

    """
    Convert:

    "83 D4 00 24 AA"

    into:

    ["83","D4","00","24","AA"]
    """


    hex_string = hex_string.strip()


    byte_list = hex_string.split()


    return byte_list



# ==========================================================
# OPERATION HEADER DECODER
# ==========================================================


def decode_op_header(op_header):


    """
    TPM SPI first byte format:

    Bit 7:
        1 = READ
        0 = WRITE


    Bits [5:0]:

        Transfer size encoding

        value = size - 1


    Example:

    0x83

    binary:

    10000011

    READ

    length = 3 + 1 = 4 bytes

    """


    value = int(
        op_header,
        16
    )


    # bit 7

    if value & 0x80:

        operation = "READ"

    else:

        operation = "WRITE"



    # lower six bits

    byte_length = (
        value & 0x3F
    ) + 1



    return operation, byte_length



# ==========================================================
# LOCALITY DECODER
# ==========================================================


def decode_locality(address_bytes):


    """
    TPM locality is encoded in the TPM address.

    Input:

    [
        D4,
        00,
        24
    ]


    Returns:

    locality number

    """


    address = (
        int(address_bytes[0],16) << 16
    ) | (
        int(address_bytes[1],16) << 8
    ) | (
        int(address_bytes[2],16)
    )


    # locality comes from TPM address region

    locality = (
        address >> 12
    ) & 0x7


    return locality



# ==========================================================
# REGISTER ADDRESS EXTRACTOR
# ==========================================================


def decode_register_addr(address_bytes):


    """
    Extract TPM 12-bit register offset.

    Example:

    D4 00 24

    Address:
    0xD40024

    Register offset:

    0x024
    """


    address = (
        int(address_bytes[0],16) << 16
    ) | (
        int(address_bytes[1],16) << 8
    ) | (
        int(address_bytes[2],16)
    )


    # lower 12 bits contain register offset

    register_addr = (
        address & 0xFFF
    )


    # keep TPM format:
    #
    # 0x000
    # 0x018
    # 0x024

    register_addr = (
        "0x" + format(
            register_addr,
            "03X"
        )
    )


    return register_addr


# ==========================================================
# MAIN STREAM CONVERTER
# ==========================================================


def convert_spi_to_stream_arr(
        interface,
        spi_string
    ):


    """
    Converts complete SPI string.

    Output:

    [
        interface,

        operation_header,

        operation_type,

        byte_length,

        locality,

        register_addr,

        payload
    ]

    """


    byte_array = hex_string_to_list(
        spi_string
    )


    operation_header = byte_array[0]


    address_bytes = byte_array[1:4]


    payload = byte_array[4:]



    operation_type, byte_length = (
        decode_op_header(
            operation_header
        )
    )


    locality = decode_locality(
        address_bytes
    )


    register_addr = decode_register_addr(
        address_bytes
    )



    stream_arr = [

        interface,

        operation_header,

        operation_type,

        byte_length,

        locality,

        register_addr,

        payload
    ]


    return stream_arr



# ==========================================================
# SELF TEST
# ==========================================================


if __name__ == "__main__":


    print("\n==============================")
    print(" SPI HEADER DECODER TEST")
    print("==============================\n")


    test_spi = (

        "83 D4 00 24 AA BB CC DD"

    )


    result = convert_spi_to_stream_arr(

        interface="FIFO",

        spi_string=test_spi
    )



    labels = [

        "Interface",

        "Operation Header",

        "Operation",

        "Byte Length",

        "Locality",

        "Register Address",

        "Payload"
    ]


    for name,value in zip(
        labels,
        result
    ):

        print(
            name,
            ":",
            value
        )


    print(
        "\nTEST COMPLETE\n"
    )