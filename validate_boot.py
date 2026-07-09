"""
validate_boot.py

Checks raw boot_seq_csv.csv against the existing SPI-STREAM
decoder functions.

This does NOT only check crashes.

It checks returned decoded output for:
    - None
    - ERROR strings
    - UNKNOWN strings
    - failed TPM decoding text

Output:
    decoder_errors.csv
"""


import csv
import os
import sys


sys.path.append(
    os.path.join(
        os.getcwd(),
        "spi_stream"
    )
)


from spi_header_decoder import convert_spi_to_stream_arr

from register_decoder import map_register

from register_payload_decoder import decode_register_payload

from tpm_command_decoder import decode_tpm_command

from tpm_response_decoder import decode_tpm_response



INPUT_FILE = "rpi_boot_csv.csv"

OUTPUT_FILE = "decoder_errors.csv"



# ----------------------------------------------------
# Helpers
# ----------------------------------------------------


def clean_byte(x):

    if x is None:
        return None

    x = x.strip()

    if x == "":
        return None

    x = x.replace("0x", "")
    x = x.replace("0X", "")

    return x.upper().zfill(2)




def bad_output(output):

    """
    Check if decoder returned failure text/object.
    """

    if output is None:
        return True


    text = str(output).lower()


    bad_words = [

        "error",
        "fail",
        "failed",
        "unable",
        "unknown",
        "exception",
        "none",
        "could not",
        "invalid"

    ]


    for word in bad_words:

        if word in text:
            return True


    return False





# ----------------------------------------------------
# Build CS based SPI transactions
# ----------------------------------------------------


def build_transactions():


    transactions=[]

    current=None


    with open(INPUT_FILE,newline="") as f:


        reader=csv.DictReader(f)


        for row in reader:


            idx=row["Index"].strip()


            if idx:


                if current:

                    transactions.append(
                        current
                    )


                current={

                    "index":idx,

                    "mosi":[],

                    "miso":[]

                }


            if current is None:

                continue



            mosi=clean_byte(
                row.get("MOSI")
            )

            miso=clean_byte(
                row.get("MISO")
            )


            if mosi:

                current["mosi"].append(
                    mosi
                )


            if miso:

                current["miso"].append(
                    miso
                )



        if current:

            transactions.append(
                current
            )


    return transactions





# ----------------------------------------------------
# Main validation
# ----------------------------------------------------


def validate(t):


    error={

        "index":t["index"],

        "stage":"PASS",

        "reason":"",

        "mosi":" ".join(t["mosi"]),

        "miso":" ".join(t["miso"])

    }



    # -------------------------------
    # SPI HEADER
    # -------------------------------


    try:


        mosi_string=" ".join(
            t["mosi"]
        )


        decoded = convert_spi_to_stream_arr(

            "FIFO",

            mosi_string

        )


        (
            reg_type,
            op_header,
            operation,
            byte_length,
            locality,
            register_addr,
            payload

        ) = decoded



    except Exception as e:


        error["stage"]="HEADER"

        error["reason"]=str(e)

        return error




    # -------------------------------
    # REGISTER
    # -------------------------------


    try:


        reg = map_register(

            reg_type,

            register_addr

        )


        if bad_output(reg):

            error["stage"]="REGISTER"

            error["reason"]=str(reg)

            return error



    except Exception as e:


        error["stage"]="REGISTER"

        error["reason"]=str(e)

        return error





    # -------------------------------
    # REGISTER PAYLOAD
    # -------------------------------


    if "FIFO" not in str(reg):


        try:


            out=decode_register_payload(

                reg,

                payload,

                operation

            )


            if bad_output(out):

                error["stage"]="REGISTER_PAYLOAD"

                error["reason"]=str(out)

                return error




        except Exception as e:


            error["stage"]="REGISTER_PAYLOAD"

            error["reason"]=str(e)

            return error




    # -------------------------------
    # TPM FIFO
    # -------------------------------


    else:


        # HOST -> TPM command


        if operation=="WRITE":


            try:


                out=decode_tpm_command(

                    payload

                )


                if bad_output(out):

                    error["stage"]="TPM_COMMAND"

                    error["reason"]=str(out)

                    return error



            except Exception as e:


                error["stage"]="TPM_COMMAND"

                error["reason"]=str(e)

                return error



        # TPM -> HOST response


        elif operation=="READ":


            try:


                # important:
                # MISO has NO SPI header.
                # remove MOSI header phase length.

                miso_payload = t["miso"][4:]



                out=decode_tpm_response(

                    miso_payload,

                    None

                )



                if bad_output(out):

                    error["stage"]="TPM_RESPONSE"

                    error["reason"]=str(out)

                    return error




            except Exception as e:


                error["stage"]="TPM_RESPONSE"

                error["reason"]=str(e)

                return error




    return error





def main():


    transactions=build_transactions()


    errors=[]


    for t in transactions:


        result=validate(t)


        if result["stage"]!="PASS":

            errors.append(result)




    with open(

        OUTPUT_FILE,

        "w",

        newline=""

    ) as f:


        writer=csv.DictWriter(

            f,

            fieldnames=[

                "index",

                "stage",

                "reason",

                "mosi",

                "miso"

            ]

        )


        writer.writeheader()


        writer.writerows(
            errors
        )



    print("="*50)

    print("VALIDATION COMPLETE")

    print("="*50)


    print(
        "Total:",
        len(transactions)
    )


    print(
        "Failures:",
        len(errors)
    )


    print(
        "Output:",
        OUTPUT_FILE
    )




if __name__=="__main__":

    main()