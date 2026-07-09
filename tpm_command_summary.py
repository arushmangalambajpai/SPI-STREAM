"""
tpm_command_summary.py


Input:
    decoded_transactions.csv


Output:
    tpm_command_summary.txt


Function:

Decoded TPM CSV
        |
        v
Collect all TPM commands
        |
        v
Count command frequency
        |
        v
List transaction indexes


Does NOT decode TPM again.
Uses transaction_csv_decoder output.
"""


import csv
from collections import defaultdict





INPUT_FILE = "decoded_transactions.csv"

OUTPUT_FILE = "tpm_command_summary.txt"





# ==========================================================
# MAIN
# ==========================================================


def main():


    commands = defaultdict(

        lambda: {

            "count":0,

            "indexes":[],

            "codes":set()

        }

    )



    total_commands = 0





    with open(

        INPUT_FILE,

        newline=""

    ) as f:



        reader = csv.DictReader(f)





        for row in reader:




            # only TPM command stream

            if row["Stream"] != "MOSI":


                continue





            cmd_name = row[

                "Cmd_Name/Response_Name"

            ].strip()



            cmd_code = row[

                "CmdCode/ResponseCode"

            ].strip()





            # skip normal register writes

            if cmd_name == "":


                continue




            # skip invalid empty commands

            if cmd_code == "":


                continue







            index = row["Index"]





            commands[cmd_name]["count"] += 1


            commands[cmd_name]["indexes"].append(

                index

            )


            commands[cmd_name]["codes"].add(

                cmd_code

            )



            total_commands += 1







    # ======================================================
    # Write summary
    # ======================================================


    with open(

        OUTPUT_FILE,

        "w"

    ) as f:




        f.write(

            "="*70

            +

            "\n"

        )


        f.write(

            "TPM COMMAND SUMMARY\n"

        )


        f.write(

            "="*70

            +

            "\n\n"

        )




        f.write(

            "Total TPM Commands Detected : "

            +

            str(total_commands)

            +

            "\n\n"

        )







        # sort by most frequent


        sorted_commands = sorted(

            commands.items(),

            key=lambda x:

                x[1]["count"],

            reverse=True

        )







        for name,data in sorted_commands:




            f.write(

                "-"*70

                +

                "\n"

            )



            f.write(

                name

                +

                "\n"

            )


            f.write(

                "-"*70

                +

                "\n"

            )




            f.write(

                "Command Code : "

                +

                ", ".join(

                    sorted(

                        data["codes"]

                    )

                )

                +

                "\n"

            )




            f.write(

                "Count        : "

                +

                str(

                    data["count"]

                )

                +

                "\n"

            )





            f.write(

                "Indexes      :\n"

            )




            # 20 indexes per line


            indexes=data["indexes"]




            for i in range(

                0,

                len(indexes),

                20

            ):



                f.write(

                    "   "

                    +

                    ", ".join(

                        indexes[i:i+20]

                    )

                    +

                    "\n"

                )






            f.write(

                "\n"

            )







    print("="*50)

    print("TPM COMMAND SUMMARY COMPLETE")

    print("="*50)



    print(

        "Unique Commands:",

        len(commands)

    )



    print(

        "Total Commands:",

        total_commands

    )



    print(

        "Output:",

        OUTPUT_FILE

    )







if __name__=="__main__":


    main()