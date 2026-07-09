"""
pcr_extend_summarise.py


Input:
    decoded_transactions.csv


Output:
    pcr_extend_summary.txt


Function:

decoded TPM CSV
        |
        v
Find TPM2_PCR_Extend commands
        |
        v
Use pcr_extend_decoder.py
        |
        v
Generate PCR extend timeline


Does NOT:
    - rebuild transactions
    - repair bytes
    - decode TPM again
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



from pcr_extend_decoder import (

    decode_pcr_extend

)





INPUT_FILE = "decoded_transactions.csv"

OUTPUT_FILE = "pcr_extend_summary.txt"






# ==========================================================
# Helpers
# ==========================================================


def format_digest(value):


    return " ".join(

        value[i:i+2]

        for i in range(

            0,

            len(value),

            2

        )

    )







def write_pcr_extend(

    f,

    index,

    result

):



    f.write(

        "\n"

    )


    f.write(

        "="*70

        +

        "\n"

    )


    f.write(

        f"TRANSACTION INDEX : {index}\n"

    )


    f.write(

        "="*70

        +

        "\n\n"

    )



    f.write(

        "Command : "

        +

        result.get(

            "command",

            ""

        )

        +

        "\n"

    )



    f.write(

        "Tag     : "

        +

        str(

            result.get(

                "tag",

                ""

            )

        )

        +

        "\n"

    )



    f.write(

        "Size    : "

        +

        str(

            result.get(

                "size",

                ""

            )

        )

        +

        "\n"

    )




    f.write(

        "\nPCR\n"

    )


    f.write(

        "PCR Index : "

        +

        str(

            result.get(

                "pcr",

                ""

            )

        )

        +

        "\n"

    )




    f.write(

        "\nDigests\n"

    )


    f.write(

        "Digest Count : "

        +

        str(

            result.get(

                "digest_count",

                ""

            )

        )

        +

        "\n\n"

    )





    for i,digest in enumerate(

        result.get(

            "digests",

            []

        )

    ):


        f.write(

            "-"*50

            +

            "\n"

        )


        f.write(

            f"Digest {i+1}\n"

        )



        f.write(

            "Algorithm : "

            +

            digest.get(

                "algorithm",

                ""

            )

            +

            "\n"

        )



        if "digest" in digest:


            f.write(

                "Value:\n"

            )


            f.write(

                format_digest(

                    digest["digest"]

                )

                +

                "\n"

            )








# ==========================================================
# Main
# ==========================================================



def main():



    detected=[]





    with open(

        INPUT_FILE,

        newline=""

    ) as f:



        reader = csv.DictReader(f)





        for row in reader:




            # ----------------------------------------------
            # Only TPM command direction
            # ----------------------------------------------

            if row["Stream"] != "MOSI":


                continue






            # ----------------------------------------------
            # Already decoded command name
            # ----------------------------------------------


            if (

                "PCR_Extend"

                not in

                row["Cmd_Name/Response_Name"]

            ):


                continue








            # ----------------------------------------------
            # Full TPM command bytes
            #
            # Reg_Payload contains:
            #
            # TAG
            # SIZE
            # COMMAND CODE
            # PAYLOAD
            #
            # exactly what decoder needs
            # ----------------------------------------------


            command = row["Reg_Payload"]






            result = decode_pcr_extend(

                command

            )





            if result["valid"]:


                detected.append(

                    (

                        int(row["Index"]),

                        result

                    )

                )









    # keep boot order


    detected.sort(

        key=lambda x:x[0]

    )







    with open(

        OUTPUT_FILE,

        "w"

    ) as f:




        f.write(

            "TPM2 PCR EXTEND SUMMARY\n"

        )



        f.write(

            "="*70

            +

            "\n"

        )



        f.write(

            "Total PCR_Extend commands detected: "

            +

            str(

                len(detected)

            )

            +

            "\n"

        )







        for index,result in detected:



            write_pcr_extend(

                f,

                index,

                result

            )








    print(

        "="*50

    )


    print(

        "PCR EXTEND SUMMARY COMPLETE"

    )


    print(

        "="*50

    )



    print(

        "Detected PCR_Extend commands:",

        len(detected)

    )



    print(

        "Output:",

        OUTPUT_FILE

    )







if __name__=="__main__":


    main()