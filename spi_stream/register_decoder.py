"""
TPM Register Decoder

Maps TPM register offsets to register names.

Input:

interface:
    FIFO / CRB

address:
    12-bit register offset

Example:

0x024

Output:

TPM_DATA_FIFO


No payload decoding happens here.
"""


# ==========================================================
# FIFO REGISTER MAP
# ==========================================================


def map_fifo_register(addr):


    value = int(
        addr,
        16
    )


    if value == 0x000:

        return "TPM_ACCESS"


    elif 0x008 <= value <= 0x00B:

        return "TPM_INT_ENABLE"


    elif value == 0x00C:

        return "TPM_INT_VECTOR"


    elif 0x010 <= value <= 0x013:

        return "TPM_INT_STATUS"


    elif 0x014 <= value <= 0x017:

        return "TPM_INTF_CAPABILITY"


    elif 0x018 <= value <= 0x01B:

        return "TPM_STS"


    elif 0x024 <= value <= 0x027:

        return "TPM_DATA_FIFO"


    elif 0x030 <= value <= 0x033:

        return "TPM_INTERFACE_ID"


    elif 0x034 <= value <= 0x037:

        return "TPM_DATA_CSUM_ENABLE"


    elif 0x038 <= value <= 0x03B:

        return "TPM_DATA_CSUM"


    elif 0x080 <= value <= 0x083:

        return "TPM_XDATA_FIFO"


    elif 0xF00 <= value <= 0xF03:

        return "TPM_DID_VID"


    elif value == 0xF04:

        return "TPM_RID"


    elif 0xF90 <= value <= 0xFFF:

        return "VENDOR_SPECIFIC_REGISTER"


    else:

        return "RESERVED"



# ==========================================================
# CRB REGISTER MAP
# ==========================================================


def map_crb_register(addr):


    value = int(
        addr,
        16
    )


    if 0x000 <= value <= 0x003:

        return "TPM_LOC_STATE"


    elif 0x008 <= value <= 0x00B:

        return "TPM_LOC_CTRL"


    elif 0x00C <= value <= 0x00F:

        return "TPM_LOC_STS"


    elif 0x010 <= value <= 0x013:

        return "TPM_DATA_CSUM_ENABLE"


    elif 0x014 <= value <= 0x017:

        return "TPM_DATA_CSUM"


    elif 0x030 <= value <= 0x037:

        return "TPM_CRB_INTF_ID"


    elif 0x040 <= value <= 0x043:

        return "TPM_CRB_CTRL_REQ"


    elif 0x044 <= value <= 0x047:

        return "TPM_CRB_CTRL_STS"


    elif 0x048 <= value <= 0x04B:

        return "TPM_CRB_CTRL_CANCEL"


    elif 0x04C <= value <= 0x04F:

        return "TPM_CRB_CTRL_START"


    elif 0x050 <= value <= 0x053:

        return "TPM_CRB_INT_ENABLE"


    elif 0x054 <= value <= 0x057:

        return "TPM_CRB_INT_STS"


    elif 0x058 <= value <= 0x05B:

        return "TPM_CRB_CTRL_CMD_SIZE"


    elif 0x05C <= value <= 0x05F:

        return "TPM_CRB_CTRL_CMD_LADDR"


    elif 0x060 <= value <= 0x063:

        return "TPM_CRB_CTRL_CMD_HADDR"


    elif 0x064 <= value <= 0x067:

        return "TPM_CRB_CTRL_RSP_SIZE"


    elif 0x068 <= value <= 0x06F:

        return "TPM_CRB_CTRL_RSP_ADDR"


    elif 0x080 <= value <= 0xEFF:

        return "TPM_CRB_DATA_BUFFER"


    else:

        return "RESERVED"



# ==========================================================
# COMMON WRAPPER
# ==========================================================


def map_register(
        interface,
        addr
    ):


    interface = interface.upper()


    if interface == "FIFO":

        return map_fifo_register(
            addr
        )


    elif interface == "CRB":

        return map_crb_register(
            addr
        )


    else:

        return "UNKNOWN_INTERFACE"



# ==========================================================
# SELF TEST
# ==========================================================


if __name__ == "__main__":


    print("\n==============================")
    print(" REGISTER DECODER TEST")
    print("==============================\n")


    tests = [

        ("FIFO","0x000"),

        ("FIFO","0x018"),

        ("FIFO","0x024"),

        ("FIFO","0xF04"),

        ("FIFO","0xFA0"),


        ("CRB","0x040"),

        ("CRB","0x080"),

        ("CRB","0x068"),

        ("CRB","0x999")

    ]



    for interface,addr in tests:


        print(

            interface,

            addr,

            " ---> ",

            map_register(
                interface,
                addr
            )
        )



    print(
        "\nTEST COMPLETE\n"
    )