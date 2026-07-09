"""
transaction_csv_decoder.py

Input:
    clean_spi_transactions.csv

Output:
    decoded_transactions.csv


Function:

Clean SPI transaction
        |
        v
Transport decode
        |
        v
Register summary
        |
        v
TPM command / response summary


Does NOT:
    - repair transactions
    - merge transactions
    - decode register bit fields
"""


import csv
import os
import sys



# ==========================================================
# Load SPI-STREAM modules
# ==========================================================


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


from tpm_command_decoder import (

    decode_tpm_command

)


from tpm_response_decoder import (

    decode_tpm_response

)





INPUT_FILE="clean_spi_transactions.csv"

OUTPUT_FILE="decoded_transactions.csv"





# ==========================================================
# Helpers
# ==========================================================


def join_bytes(data):


    if data is None:

        return ""


    return " ".join(data)





def safe_get(d,key):


    if isinstance(d,dict):

        return d.get(
            key,
            ""
        )


    return ""





def get_command_payload(payload):


    # TAG(2)+SIZE(4)+CC(4)


    if len(payload)>10:

        return payload[10:]


    return []





def make_empty_row(index,stream):


    return {


        "Index":index,

        "Stream":stream,

        "OpDirn":"",

        "ByteSize":"",

        "Locality":"",

        "Reg_Addr":"",

        "Reg_Name":"",

        "Reg_Payload":"",

        "Tag":"",

        "CmdSize":"",

        "CmdCode/ResponseCode":"",

        "Cmd_Name/Response_Name":"",

        "Cmd_Payload/Response_Payload":""


    }








# ==========================================================
# Decode one stream
# ==========================================================



def decode_stream(index,stream_name,mosi,miso):


    row=make_empty_row(

        index,

        stream_name

    )



    try:



        (

            reg_type,

            op_header,

            operation,

            byte_size,

            locality,

            reg_addr,

            payload


        ) = convert_spi_to_stream_arr(

            "FIFO",

            " ".join(mosi)

        )



    except Exception as e:



        row["Reg_Name"]="SPI_PARSE_ERROR"


        return row






    # ======================================================
    # Common transport fields
    # ======================================================


    row["OpDirn"]=operation

    row["ByteSize"]=byte_size

    row["Locality"]=locality

    row["Reg_Addr"]=reg_addr





    # Register name


    try:


        reg_name=map_register(

            reg_type,

            reg_addr

        )


    except:


        reg_name="UNKNOWN_REGISTER"




    row["Reg_Name"]=str(reg_name)





    # ======================================================
    # MOSI STREAM
    # ======================================================


    if stream_name=="MOSI":


        # use actual bytes after SPI header

        mosi_payload = mosi[4:]


        row["Reg_Payload"]=join_bytes(

            mosi_payload

        )



        # --------------------------------------------------
        # TPM command detection
        #
        # Do NOT depend on operation.
        #
        # Some TPM SPI transactions appear as READ
        # but contain command bytes on MOSI.
        # --------------------------------------------------


        is_tpm_command = False



        if len(mosi_payload) >= 10:


            if mosi_payload[:2] in [

                ["80","01"],

                ["80","02"],

                ["C0","01"],

                ["C0","02"]

            ]:


                is_tpm_command=True






        if (

            "FIFO" in str(reg_name)

            and

            is_tpm_command

        ):



            cmd=decode_tpm_command(

                mosi_payload

            )





            row["Tag"]=safe_get(

                cmd,

                "tag"

            )



            row["CmdSize"]=safe_get(

                cmd,

                "cmd_size"

            )



            row["CmdCode/ResponseCode"]=safe_get(

                cmd,

                "cmd_code"

            )



            row["Cmd_Name/Response_Name"]=safe_get(

                cmd,

                "cmd_name"

            )



            row["Cmd_Payload/Response_Payload"]=join_bytes(

                get_command_payload(

                    mosi_payload

                )

            )




    # ======================================================
    # MISO STREAM
    # ======================================================


    else:



        # MISO data after SPI header


        miso_payload=miso[4:]



        row["Reg_Payload"]=join_bytes(

            miso_payload

        )






        if (

            "FIFO" in str(reg_name)

            and

            operation=="READ"

        ):




            rsp=decode_tpm_response(

                miso_payload,

                None

            )




            row["Tag"]=safe_get(

                rsp,

                "tag"

            )



            row["CmdSize"]=safe_get(

                rsp,

                "response_size"

            )



            row["CmdCode/ResponseCode"]=safe_get(

                rsp,

                "response_code"

            )



            row["Cmd_Name/Response_Name"]=safe_get(

                rsp,

                "response_name"

            )



            row["Cmd_Payload/Response_Payload"]=join_bytes(

                get_command_payload(

                    miso_payload

                )

            )






    return row









# ==========================================================
# MAIN
# ==========================================================


def main():



    decoded=[]




    with open(

        INPUT_FILE,

        newline=""

    ) as f:



        reader=csv.DictReader(f)



        for r in reader:



            index=r["Index"]



            mosi=r["MOSI"].split()

            miso=r["MISO"].split()





            decoded.append(


                decode_stream(

                    index,

                    "MOSI",

                    mosi,

                    miso

                )


            )






            decoded.append(


                decode_stream(

                    index,

                    "MISO",

                    mosi,

                    miso

                )


            )







    with open(

        OUTPUT_FILE,

        "w",

        newline=""

    ) as f:



        writer=csv.DictWriter(

            f,

            fieldnames=[

                "Index",

                "Stream",

                "OpDirn",

                "ByteSize",

                "Locality",

                "Reg_Addr",

                "Reg_Name",

                "Reg_Payload",

                "Tag",

                "CmdSize",

                "CmdCode/ResponseCode",

                "Cmd_Name/Response_Name",

                "Cmd_Payload/Response_Payload"

            ]

        )



        writer.writeheader()


        writer.writerows(

            decoded

        )






    print("="*50)

    print("TRANSACTION CSV DECODER COMPLETE")

    print("="*50)


    print(

        "Rows written:",

        len(decoded)

    )


    print(

        "Saved:",

        OUTPUT_FILE

    )








if __name__=="__main__":


    main()