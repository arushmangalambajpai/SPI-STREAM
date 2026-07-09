"""
SPI-STREAM MAIN DECODER

Final integration layer.

SPI transaction
        |
        v
Header Decode
        |
        v
Register Decode
        |
        v
Payload Decode
        |
        +--> Register Object
        |
        +--> TPM Object
"""


# ==========================================================
# IMPORTS
# ==========================================================


from class_structure import (

    MOSI_REG,
    MISO_REG,

    MOSI_TPM,
    MISO_TPM

)


from spi_header_decoder import (

    convert_spi_to_stream_arr

)


from register_decoder import (

    map_register

)


from register_payload_decoder import (

    decode_register_payload

)


from tpm_command_decoder import (

    decode_tpm_command

)


from tpm_response_decoder import (

    decode_tpm_response

)



# ==========================================================
# TPM DATA REGISTER CHECK
# ==========================================================


def is_tpm_data_register(reg_name):


    return reg_name in [

        "TPM_DATA_FIFO",

        "TPM_XDATA_FIFO",

        "TPM_CRB_DATA_BUFFER"

    ]




# ==========================================================
# MOSI DECODER
# ==========================================================


def decode_mosi(
        spi_string,
        interface
    ):


    stream = convert_spi_to_stream_arr(

        interface,

        spi_string

    )


    (

        reg_type,

        op_header,

        operation,

        byte_length,

        locality,

        register_addr,

        payload

    ) = stream



    reg_name = map_register(

        reg_type,

        register_addr

    )



    reg_payload_decoded = decode_register_payload(

        reg_name,

        payload,

        operation

    )



    base = (

        reg_type,

        operation,

        byte_length,

        locality,

        register_addr,

        reg_name,

        payload,

        reg_payload_decoded

    )



    # ==============================
    # TPM COMMAND
    # ==============================


    if (

        operation == "WRITE"

        and

        is_tpm_data_register(reg_name)

    ):


        decoded = decode_tpm_command(

            payload

        )



        return MOSI_TPM(

            *base,


            tag =
            decoded["tag"],


            cmd_size =
            decoded["cmd_size"],


            cmd_code =
            decoded["cmd_code"],


            cmd_name =
            decoded["cmd_name"],


            tpm_payload_decoded_op =
            decoded["tree"]

        )



    # normal register


    return MOSI_REG(

        *base

    )





# ==========================================================
# FULL TRANSACTION DECODER
# ==========================================================


def decode_transaction(

        mosi,

        miso,

        interface,

        command_code=None

    ):



    mosi_obj = decode_mosi(

        mosi,

        interface

    )



    # WRITE:
    #
    # useful payload already in MOSI


    if mosi_obj.operation_type == "WRITE":


        return (

            mosi_obj,

            None

        )




    # READ:
    #
    # decode MISO payload


    miso_stream = convert_spi_to_stream_arr(

        interface,

        miso

    )



    miso_payload = miso_stream[-1]



    decoded_payload = decode_register_payload(

        mosi_obj.reg_name,

        miso_payload,

        "READ"

    )



    base = (

        mosi_obj.reg_type,

        "READ",

        mosi_obj.byte_length,

        mosi_obj.locality,

        mosi_obj.register_addr,

        mosi_obj.reg_name,

        miso_payload,

        decoded_payload

    )



    # ==============================
    # TPM RESPONSE
    # ==============================


    if is_tpm_data_register(

        mosi_obj.reg_name

    ):



        decoded = decode_tpm_response(

            miso_payload,

            command_code

        )



        miso_obj = MISO_TPM(

            *base,


            tag =
            decoded["tag"],


            response_size =
            decoded["response_size"],


            response_code =
            decoded["response_code"],


            response_name =
            decoded["response_name"],


            tpm_response_decoded_op =
            decoded["tree"]

        )



    else:


        miso_obj = MISO_REG(

            *base

        )



    return (

        mosi_obj,

        miso_obj

    )





# ==========================================================
# COMPLETE PIPELINE TEST
# ==========================================================


if __name__ == "__main__":


    print("\nSPI-STREAM FULL PIPELINE TEST\n")


    tests = [


        # ==================================================
        # 1. FIFO NORMAL REGISTER TEST
        # TPM_STS WRITE commandReady
        # ==================================================

        (
            "FIFO TPM_STS WRITE",

            lambda:

            decode_mosi(

                "23 D4 00 18 40 00 00 00",

                "FIFO"

            )

        ),



        # ==================================================
        # 2. TPM2_STARTUP COMMAND
        # ==================================================

        (

            "TPM2_STARTUP COMMAND",

            lambda:

            decode_mosi(

                "2B D4 00 24 "

                "80 01 "

                "00 00 00 0C "

                "00 00 01 44 "

                "00 00",

                "FIFO"

            )

        ),




        # ==================================================
        # 3. TPM2_GET_RANDOM COMMAND
        # ==================================================


        (

            "TPM2_GET_RANDOM COMMAND",

            lambda:

            decode_mosi(

                "2B D4 00 24 "

                "80 01 "

                "00 00 00 0C "

                "00 00 01 7B "

                "00 10",

                "FIFO"

            )

        ),





        # ==================================================
        # 4. TPM2_GET_CAPABILITY COMMAND
        # ==================================================


        (

            "TPM2_GET_CAPABILITY COMMAND",

            lambda:

            decode_mosi(

                "35 D4 00 24 "

                "80 01 "

                "00 00 00 16 "

                "00 00 01 7A "

                "00 00 00 06 "

                "00 00 01 05 "

                "00 00 00 08",

                "FIFO"

            )

        ),





        # ==================================================
        # 5. TPM2_PCR_READ COMMAND
        # ==================================================


        (

            "TPM2_PCR_READ COMMAND",

            lambda:

            decode_mosi(

                "33 D4 00 24 "

                "80 01 "

                "00 00 00 14 "

                "00 00 01 7E "

                "00 00 00 01 "

                "00 0B "

                "03 "

                "00 00 01",

                "FIFO"

            )

        ),






        # ==================================================
        # 6. TPM2_GET_RANDOM RESPONSE
        # ==================================================

        (

            "TPM2_GET_RANDOM RESPONSE",

            lambda:

            decode_transaction(


                # MOSI READ FIFO

                "8F D4 00 24",



                # MISO response

                "00 00 00 00 "

                "80 01 "

                "00 00 00 1C "

                "00 00 00 00 "

                "00 10 "

                "11 22 33 44 "

                "55 66 77 88 "

                "99 AA BB CC "

                "DD EE FF 00",


                "FIFO",


                "TPM_CC.GetRandom"

            )[1]

        ),






        # ==================================================
        # 7. TPM2_GET_CAPABILITY RESPONSE
        # ==================================================

        (

            "TPM2_GET_CAPABILITY RESPONSE",

            lambda:

            decode_transaction(


                "8F D4 00 24",


                "00 00 00 00 "

                "80 01 "

                "00 00 00 1B "

                "00 00 00 00 "

                "00 "

                "00 00 00 06 "

                "00 00 00 01 "

                "00 00 01 05 "

                "49 46 58 00",



                "FIFO",


                "TPM_CC.GetCapability"

            )[1]

        )

    ]




    for name,func in tests:


        print("\n\n===================================")

        print(name)

        print("===================================")



        try:


            obj = func()


            obj.show()



        except Exception as e:


            print(

                "FAILED:",

                e

            )



    print(

        "\nALL SPI PIPELINE TESTS COMPLETE\n"

    ) 