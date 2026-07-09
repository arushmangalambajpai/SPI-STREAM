"""
check_command_sizes.py

Temporary checker.

Checks:
TPM commandSize field == actual bytes
in clean_spi_transactions.csv

No modifications.
"""


import csv



TPM_TAGS = [

    ["80","01"],

    ["80","02"],

    ["C0","01"],

    ["C0","02"]

]



bad=[]



with open(
    "clean_spi_transactions.csv",
    newline=""
) as f:


    reader=csv.DictReader(f)



    for row in reader:


        mosi=row["MOSI"].split()


        # remove SPI header
        payload=mosi[4:]



        if len(payload)<10:

            continue



        if payload[:2] not in TPM_TAGS:

            continue




        expected=int(

            "".join(
                payload[2:6]
            ),

            16

        )



        actual=len(payload)




        if expected != actual:


            bad.append(

                [

                    row["Index"],

                    expected,

                    actual,

                    expected-actual,

                    " ".join(payload)

                ]

            )





print("="*50)

print("TPM COMMAND SIZE CHECK")

print("="*50)



print(
    "Problems:",
    len(bad)
)



for b in bad:


    print()

    print(
        "Index:",
        b[0]
    )


    print(
        "Expected:",
        b[1]
    )


    print(
        "Actual:",
        b[2]
    )


    print(
        "Missing:",
        b[3]
    )


    print(
        "Payload:"
    )


    print(
        b[4]
    )