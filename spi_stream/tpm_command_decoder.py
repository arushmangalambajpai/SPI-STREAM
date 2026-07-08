"""
TPM Command Decoder

Wrapper around tpmstream.

Input:

TPM command byte stream

Example:

80 01 00 00 00 0C 00 00 01 44 00 00


Output:

{
    tag,
    cmd_size,
    cmd_code,
    cmd_name,
    tree
}


Used later by MOSI_TPM object.
"""


# ==========================================================
# IMPORT TPMSTREAM
# ==========================================================


try:

    from tpmstream.io.auto import Auto

    from tpmstream.io.pretty import Pretty

    from tpmstream.common.object import events_to_objs

    from tpmstream.spec.commands import Command


    TPMSTREAM_AVAILABLE = True


except Exception as e:


    TPMSTREAM_AVAILABLE = False





# ==========================================================
# PAYLOAD CONVERTER
# ==========================================================


def payload_to_bytes(payload):


    """
    Accept:

    ["80","01"]

    or

    "80 01"


    Return:

    bytes
    """


    if isinstance(payload, list):

        hex_string = "".join(payload)


    else:

        hex_string = payload.replace(
            " ",
            ""
        )


    return bytes.fromhex(
        hex_string
    )





# ==========================================================
# FALLBACK COMMAND HEADER DECODER
# ==========================================================


def manual_command_header_decode(payload):


    data = payload_to_bytes(
        payload
    )


    if len(data) < 10:


        return {

            "tag":
                None,

            "cmd_size":
                None,

            "cmd_code":
                None,

            "cmd_name":
                "INVALID_TPM_COMMAND"

        }



    tag = int.from_bytes(

        data[0:2],

        "big"

    )


    size = int.from_bytes(

        data[2:6],

        "big"

    )


    command_code = int.from_bytes(

        data[6:10],

        "big"

    )



    return {

        "tag":
            hex(tag),


        "cmd_size":
            size,


        "cmd_code":
            hex(command_code),


        "cmd_name":
            "UNKNOWN_TPM_COMMAND"

    }






# ==========================================================
# TPMSTREAM TREE DECODER
# ==========================================================

def get_tpmstream_tree(payload):


    if not TPMSTREAM_AVAILABLE:


        return "tpmstream unavailable"



    try:


        data = payload_to_bytes(
            payload
        )



        events = Auto.marshal(

            tpm_type = Command,

            buffer = data,

            abort_on_error = False

        )



        tree_generator = Pretty.unmarshal(

            events

        )



        tree = ""


        for line in tree_generator:


            tree += str(line)

            tree += "\n"



        return tree



    except Exception as e:


        return (

            "Unable to generate TPM tree: "

            +

            str(e)

        )






# ==========================================================
# MAIN COMMAND DECODER
# ==========================================================


def decode_tpm_command(payload):


    """
    Main external function.

    Used by decode_spi.py
    """



    # Always get header manually first

    output = manual_command_header_decode(

        payload

    )



    # Add tree output

    output["tree"] = get_tpmstream_tree(

        payload

    )



    if not TPMSTREAM_AVAILABLE:


        return output




    try:


        data = payload_to_bytes(

            payload

        )



        events = Auto.marshal(

            tpm_type = Command,

            buffer = data,

            abort_on_error = False

        )



        objects = list(

            events_to_objs(events)

        )



        command = objects[0]



        # --------------------------
        # Extract fields
        # --------------------------


        output["tag"] = str(

            command.tag

        )



        output["cmd_size"] = int(

            command.commandSize

        )



        output["cmd_code"] = str(

            command.commandCode

        )



        #
        # TPM_CC.Startup
        #       |
        #       v
        # Startup
        #


        name = str(

            command.commandCode

        )


        if "." in name:


            name = name.split(".")[-1]



        output["cmd_name"] = name




    except Exception:


        # fallback values remain

        pass




    return output







# ==========================================================
# SELF TEST
# ==========================================================
# ==========================================================
# SELF TEST
# ==========================================================


if __name__ == "__main__":


    print(
        "\nTPM COMMAND DECODER FULL TEST\n"
    )


    test_commands = {


        # ==========================================
        # TPM2_Startup
        #
        # TPM_CC = 00000144
        # ==========================================

        "TPM2_Startup":

        [

            "80","01",

            "00","00","00","0C",

            "00","00","01","44",

            "00","00"

        ],



        # ==========================================
        # TPM2_GetRandom
        #
        # TPM_CC = 0000017B
        #
        # Ask TPM for 16 random bytes
        # ==========================================


        "TPM2_GetRandom":

        [

            "80","01",

            "00","00","00","0C",

            "00","00","01","7B",

            "00","10"

        ],




        # ==========================================
        # TPM2_PCR_Read
        #
        # TPM_CC = 0000017E
        #
        # Read PCR values
        # ==========================================


        "TPM2_PCR_Read":

        [

            "80","01",

            "00","00","00","14",

            "00","00","01","7E",


            # count

            "00","00","00","01",


            # hash algorithm SHA256

            "00","0B",


            # sizeofSelect

            "03",


            # PCR bitmap

            "00","00","01"

        ],





        # ==========================================
        # TPM2_PCR_Extend
        #
        # TPM_CC = 00000182
        #
        # PCR Handle:
        # PCR 0
        #
        # SHA256 digest
        #
        # ==========================================


        "TPM2_PCR_Extend_SHA256":

        [
        
            # tag with sessions

            "80","02",


            # size = 65 bytes

            "00","00","00","41",


            # TPM_CC_PCR_Extend

            "00","00","01","82",


            # PCR handle 0

            "00","00","00","00",



            # authorizationSize = 9

            "00","00","00","09",


            # sessionHandle = password session

            "40","00","00","09",


            # nonce size

            "00","00",


            # session attributes

            "00",


            # hmac size

            "00","00",



            # digest count

            "00","00","00","01",


            # hash algorithm SHA256

            "00","0B",



            # SHA256 digest (32 bytes)

            "11","11","11","11",

            "22","22","22","22",

            "33","33","33","33",

            "44","44","44","44",

            "55","55","55","55",

            "66","66","66","66",

            "77","77","77","77",

            "88","88","88","88"

        ],
        # ==========================================
        # TPM2_GetCapability
        #
        # TPM_CC = 0000017A
        #
        # Query TPM properties
        #
        # capability:
        # TPM_CAP_TPM_PROPERTIES
        #
        # property:
        # TPM_PT_MANUFACTURER
        #
        # count:
        # 8
        # ==========================================


        "TPM2_GetCapability":

        [

            # TPM_ST_NO_SESSIONS

            "80","01",


            # size = 22 bytes

            "00","00","00","16",


            # TPM_CC_GetCapability

            "00","00","01","7A",



            # capability
            # TPM_CAP_TPM_PROPERTIES
            # 0x00000006

            "00","00","00","06",



            # property
            # TPM_PT_MANUFACTURER
            # 0x00000105

            "00","00","01","05",



            # propertyCount

            "00","00","00","08"

        ],

        # ==========================================
        # TPM2_PCR_Extend
        #
        # Two digests:
        #
        # SHA1   (20 bytes)
        # SHA256 (32 bytes)
        #
        # Tests TPMU_HA selector parsing
        # ==========================================


        "TPM2_PCR_Extend_SHA1_SHA256":

        [

            # TPM_ST_SESSIONS

            "80","02",


            # size = 87 bytes

            "00","00","00","57",


            # TPM_CC_PCR_Extend

            "00","00","01","82",


            # PCR Handle PCR0

            "00","00","00","00",



            # authorizationSize = 9

            "00","00","00","09",


            # sessionHandle = TPM_RS_PW

            "40","00","00","09",


            # nonce size = 0

            "00","00",


            # session attributes

            "00",


            # hmac size = 0

            "00","00",



            # =============================
            # TPML_DIGEST_VALUES
            # =============================


            # count = 2

            "00","00","00","02",



            # -----------------------------
            # Digest 1
            # SHA1
            # -----------------------------


            # TPM_ALG_SHA1

            "00","04",



            # SHA1 digest
            # 20 bytes


            "11","11","11","11",

            "22","22","22","22",

            "33","33","33","33",

            "44","44","44","44",

            "55","55","55","55",



            # -----------------------------
            # Digest 2
            # SHA256
            # -----------------------------


            # TPM_ALG_SHA256

            "00","0B",



            # SHA256 digest
            # 32 bytes


            "AA","AA","AA","AA",

            "BB","BB","BB","BB",

            "CC","CC","CC","CC",

            "DD","DD","DD","DD",

            "EE","EE","EE","EE",

            "FF","FF","FF","FF",

            "12","12","12","12",

            "34","34","34","34"

        ],

        # ==========================================
        # Unknown vendor command
        #
        # Tests fallback
        # ==========================================


        "UNKNOWN_COMMAND":

        [

            "80","01",

            "00","00","00","0A",

            "20","00","00","00"

        ]


    }



    for name,command in test_commands.items():


        print("\n================================")
        print(name)
        print("================================")



        result = decode_tpm_command(

            command

        )



        print(

            "TAG :",

            result["tag"]

        )



        print(

            "SIZE:",

            result["cmd_size"]

        )



        print(

            "CODE:",

            result["cmd_code"]

        )



        print(

            "NAME:",

            result["cmd_name"]

        )



        print(

            "\nTREE:\n"

        )



        print(

            result["tree"]

        )



    print(

        "\nALL COMMAND TESTS COMPLETE\n"

    )