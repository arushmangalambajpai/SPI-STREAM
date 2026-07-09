"""
validate_transactions.py

Temporary validator AFTER transaction builder.

Input:
    clean_spi_transactions.csv

Output:
    decoder_errors.csv


Checks whether each built SPI transaction can be decoded
by the existing SPI-STREAM pipeline.

Only detects STRUCTURAL failures.

Does NOT fail because:
    - UNKNOWN_TPM_COMMAND
    - tpmstream tree errors
"""


import csv
import os
import sys



# -------------------------------------------------------
# Load SPI-STREAM modules
# -------------------------------------------------------


sys.path.append(
    os.path.join(
        os.getcwd(),
        "spi_stream"
    )
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




INPUT_FILE = "clean_spi_transactions.csv"

OUTPUT_FILE = "decoder_errors.csv"





# =======================================================
# Error detection
# =======================================================


def is_bad_output(output):


    if output is None:

        return True




    # ==================================================
    # TPM COMMAND OUTPUT
    # ==================================================


    if isinstance(output, dict):


        if "cmd_size" in output:


            if output.get("tag") is None:

                return True



            try:

                size = int(
                    output.get("cmd_size")
                )

            except:

                return True




            if size < 10 or size > 4096:

                return True




            if output.get("cmd_code") is None:

                return True




            return False







        # ==============================================
        # TPM RESPONSE OUTPUT
        # ==============================================


        if "response_size" in output:


            if output.get("tag") is None:

                return True




            try:

                size = int(

                    output.get(
                        "response_size"
                    )

                )


            except:

                return True




            if size < 10 or size > 4096:

                return True




            if output.get("response_code") is None:

                return True




            return False







    # ==================================================
    # STRING BASED FAILURES
    # ==================================================


    text=str(output).lower()



    bad_words=[

        "failed",

        "could not",

        "exception",

        "invalid"

    ]




    for word in bad_words:


        if word in text:

            return True





    return False








# =======================================================
# Load transactions
# =======================================================


def load_transactions():



    transactions=[]



    with open(

        INPUT_FILE,

        newline=""

    ) as f:



        reader=csv.DictReader(f)




        for row in reader:



            transactions.append({


                "index":

                    row["Index"],



                "mosi":

                    row["MOSI"].split(),



                "miso":

                    row["MISO"].split()

            })




    return transactions







# =======================================================
# Validate one transaction
# =======================================================


def validate(t):


    error={


        "index":t["index"],

        "stage":"PASS",

        "operation":"",

        "register":"",

        "reason":"",

        "mosi":" ".join(
            t["mosi"]
        ),

        "miso":" ".join(
            t["miso"]
        )

    }




    # ---------------------------------------------------
    # SPI HEADER
    # ---------------------------------------------------


    try:


        (

            reg_type,

            op_header,

            operation,

            byte_length,

            locality,

            register_addr,

            payload


        ) = convert_spi_to_stream_arr(


            "FIFO",


            " ".join(

                t["mosi"]

            )

        )



        error["operation"]=operation




    except Exception as e:



        error["stage"]="SPI_HEADER"

        error["reason"]=str(e)

        return error








    # ---------------------------------------------------
    # REGISTER
    # ---------------------------------------------------


    try:



        register=map_register(

            reg_type,

            register_addr

        )



        error["register"]=str(register)




        if is_bad_output(register):


            error["stage"]="REGISTER"

            error["reason"]=str(register)

            return error




    except Exception as e:



        error["stage"]="REGISTER"

        error["reason"]=str(e)

        return error







    # ---------------------------------------------------
    # NORMAL REGISTER PAYLOAD
    # ---------------------------------------------------



    if "FIFO" not in str(register):


        try:



            out=decode_register_payload(

                register,

                payload,

                operation

            )




            if is_bad_output(out):


                error["stage"]="REGISTER_PAYLOAD"

                error["reason"]=str(out)

                return error




        except Exception as e:



            error["stage"]="REGISTER_PAYLOAD"

            error["reason"]=str(e)

            return error








    # ---------------------------------------------------
    # DATA FIFO
    # ---------------------------------------------------



    else:



        if operation=="WRITE":



            try:



                out=decode_tpm_command(

                    payload

                )




                if is_bad_output(out):


                    error["stage"]="TPM_COMMAND"

                    error["reason"]=str(out)

                    return error





            except Exception as e:



                error["stage"]="TPM_COMMAND"

                error["reason"]=str(e)

                return error







        elif operation=="READ":




            try:



                miso_payload = t["miso"][4:]



                out=decode_tpm_response(

                    miso_payload,

                    None

                )




                if is_bad_output(out):


                    error["stage"]="TPM_RESPONSE"

                    error["reason"]=str(out)

                    return error





            except Exception as e:



                error["stage"]="TPM_RESPONSE"

                error["reason"]=str(e)

                return error







    return error









# =======================================================
# MAIN
# =======================================================



def main():



    transactions=load_transactions()



    errors=[]





    for t in transactions:



        result=validate(t)




        if result["stage"]!="PASS":



            errors.append(

                result

            )







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

                "operation",

                "register",

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

    print("TRANSACTION VALIDATION COMPLETE")

    print("="*50)



    print(

        "Transactions:",

        len(transactions)

    )



    print(

        "Errors:",

        len(errors)

    )



    print(

        "Output:",

        OUTPUT_FILE

    )







if __name__=="__main__":

    main()