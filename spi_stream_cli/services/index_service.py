"""
Decode Transaction By Index

Uses:

clean_spi_transactions.csv

Finds:
    Index

Extracts:
    MOSI
    MISO

Runs:
    decode_transaction()
"""


import csv


from spi_stream_cli.services.decode_service import (

    run_transaction_decode

)





def decode_index(

    index,

    interface="FIFO",

    file="clean_spi_transactions.csv"

):


    with open(

        file,

        newline=""

    ) as f:


        reader=csv.DictReader(f)



        for row in reader:



            if row["Index"] == str(index):


                mosi=row["MOSI"]

                miso=row["MISO"]



                return run_transaction_decode(

                    interface,

                    mosi,

                    miso

                )





    return (

        "Transaction index not found: "

        +

        str(index)

    )