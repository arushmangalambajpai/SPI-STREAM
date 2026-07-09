"""
TPM2 PCR Extend Decoder

Special semantic decoder.

Input:
    Raw TPM2_PCR_Extend command bytes

Output:
    PCR handle
    Hash algorithms
    Digest values


Only handles:

TPM_CC_PCR_Extend = 0x00000182
"""


# ==========================================================
# HASH ALG MAP
# ==========================================================


HASH_ALGS = {

    0x0004:
    (
        "SHA1",
        20
    ),


    0x000B:
    (
        "SHA256",
        32
    ),


    0x000C:
    (
        "SHA384",
        48
    ),


    0x000D:
    (
        "SHA512",
        64
    )

}





# ==========================================================
# HELPERS
# ==========================================================


def bytes_to_int(data):


    return int.from_bytes(

        bytes(data),

        "big"

    )





def clean_input(data):


    if isinstance(data,str):

        return [

            int(x,16)

            for x in data.split()

        ]


    return data





# ==========================================================
# MAIN DECODER
# ==========================================================


def decode_pcr_extend(command):


    data = clean_input(command)



    output = {

        "valid":False,

        "pcr":None,

        "digests":[]

    }



    # --------------------------------
    # TPM Header
    # --------------------------------


    tag = bytes_to_int(

        data[0:2]

    )


    size = bytes_to_int(

        data[2:6]

    )


    command_code = bytes_to_int(

        data[6:10]

    )



    if command_code != 0x00000182:


        output["error"] = (

            "Not TPM2_PCR_Extend"

        )


        return output



    output["valid"] = True


    output["tag"] = hex(tag)

    output["size"] = size

    output["command"] = "TPM2_PCR_Extend"




    # --------------------------------
    # HANDLE AREA
    # --------------------------------


    offset = 10



    pcr_handle = bytes_to_int(

        data[offset:offset+4]

    )


    output["pcr"] = pcr_handle


    offset += 4





    # --------------------------------
    # AUTH AREA
    #
    # only exists for 8002 sessions
    # --------------------------------


    if tag == 0x8002:



        auth_size = bytes_to_int(

            data[offset:offset+4]

        )


        offset += 4


        # skip authorization area


        offset += auth_size





    # --------------------------------
    # TPML_DIGEST_VALUES
    # --------------------------------


    digest_count = bytes_to_int(

        data[offset:offset+4]

    )


    offset += 4



    output["digest_count"] = digest_count





    for i in range(digest_count):



        alg_id = bytes_to_int(

            data[offset:offset+2]

        )


        offset += 2



        if alg_id not in HASH_ALGS:


            output["digests"].append(

                {

                "algorithm":

                "UNKNOWN",


                "alg_id":

                hex(alg_id)

                }

            )


            break




        alg_name, digest_size = HASH_ALGS[alg_id]



        digest = data[

            offset:

            offset + digest_size

        ]



        offset += digest_size




        digest_hex = "".join(

            f"{x:02X}"

            for x in digest

        )




        output["digests"].append(

            {

            "algorithm":

            alg_name,


            "digest":

            digest_hex

            }

        )




    return output


# ==========================================================
# PRETTY OUTPUT
# ==========================================================


def pretty_print_pcr_extend(command):


    result = decode_pcr_extend(command)



    if result["valid"] == False:


        print("\nINVALID PCR EXTEND COMMAND")

        print(
            result.get(
                "error",
                ""
            )
        )


        return




    print("\n")

    print("=" * 60)

    print("                 TPM2 PCR EXTEND")

    print("=" * 60)



    print(
        "\nCommand Information\n"
    )


    print(
        "TPM Command      :",
        result["command"]
    )


    print(
        "Command Tag      :",
        result["tag"]
    )


    print(
        "Command Size     :",
        result["size"],
        "bytes"
    )



    print(
        "\nPCR Information\n"
    )


    print(
        "PCR Index        :",
        result["pcr"]
    )


    print(
        "Digest Count     :",
        result["digest_count"]
    )





    print(

        "\nDigest Values\n"

    )



    for index,digest in enumerate(

        result["digests"]

    ):


        print(

            "-" * 60

        )


        print(

            "Digest",

            index + 1

        )


        print(

            "-" * 60

        )



        print(

            "Algorithm        :",

            digest["algorithm"]

        )



        if "digest" in digest:


            value = digest["digest"]



            # split long digest

            pretty_digest = " ".join(

                value[i:i+2]

                for i in range(
                    0,
                    len(value),
                    2
                )

            )



            print(

                "Digest Length    :",

                len(value)//2,

                "bytes"

            )



            print(

                "Digest Value     :"

            )



            # print 16 bytes per line


            for i in range(

                0,

                len(pretty_digest),

                48

            ):


                print(

                    "   ",

                    pretty_digest[i:i+48]

                )




    print(

        "\n"

        +

        "="*60

    )





# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":


    print(

        "\nPCR EXTEND DECODER TEST\n"

    )


    cmd = (

        # ==================================================
        # TPM HEADER
        # ==================================================

        # TPM_ST_SESSIONS

        "80 02 "


        # command size = 87 bytes

        "00 00 00 57 "


        # TPM_CC_PCR_EXTEND

        "00 00 01 82 "



        # ==================================================
        # HANDLE AREA
        # ==================================================

        # PCR handle PCR0

        "00 00 00 00 "




        # ==================================================
        # AUTH AREA
        # ==================================================

        # authSize = 9 bytes

        "00 00 00 09 "


        # sessionHandle TPM_RS_PW

        "40 00 00 09 "


        # nonce size = 0

        "00 00 "


        # session attributes

        "00 "


        # hmac size = 0

        "00 00 "




        # ==================================================
        # TPML_DIGEST_VALUES
        # ==================================================

        # digest count = 2

        "00 00 00 02 "




        # --------------------------------------------------
        # DIGEST 1 : SHA1
        # --------------------------------------------------

        # TPM_ALG_SHA1

        "00 04 "


        # SHA1 digest (20 bytes)

        "11 11 11 11 "

        "22 22 22 22 "

        "33 33 33 33 "

        "44 44 44 44 "

        "55 55 55 55 "




        # --------------------------------------------------
        # DIGEST 2 : SHA256
        # --------------------------------------------------

        # TPM_ALG_SHA256

        "00 0B "


        # SHA256 digest (32 bytes)

        "AA AA AA AA "

        "BB BB BB BB "

        "CC CC CC CC "

        "DD DD DD DD "

        "EE EE EE EE "

        "FF FF FF FF "

        "12 12 12 12 "

        "34 34 34 34"

    )



    pretty_print_pcr_extend(

        cmd

    )