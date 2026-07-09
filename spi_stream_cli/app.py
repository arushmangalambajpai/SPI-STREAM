"""
SPI-STREAM CLI Application
"""


from spi_stream_cli.ui.splash import show_splash

from spi_stream_cli.ui.menu import menu

from spi_stream_cli.ui.input import get_input

from spi_stream_cli.ui.viewer import viewer
from spi_stream_cli.ui.file_picker import select_file
from spi_stream_cli.services.csv_service import (

    generate_clean_transactions,

    generate_decoded_transactions,

    generate_command_summary,

    generate_pcr_summary

)
from spi_stream_cli.services.index_service import (

    decode_index

)
from spi_stream_cli.services.decode_service import (

    run_mosi_decode,

    run_transaction_decode

)








def main():


    show_splash()



    while True:


        choice=menu(

            "SPI-STREAM",

            [

                "Decode SPI Transaction",

                "Decode Boot Sequence CSV",

                "Exit"

            ],

            """

TPM SPI Analysis Toolkit

✓ FIFO Support
✓ CRB Support

"""

        )




        if choice=="Decode SPI Transaction":


            transaction_menu()



        elif choice=="Decode Boot Sequence CSV":


            csv_menu()



        else:


            break










def transaction_menu():


    interface=menu(

        "Select TPM Interface",

        [

            "FIFO",

            "CRB",

            "Back"

        ]

    )



    if interface=="Back":

        return





    mode=menu(

        "Decode Mode",

        [

            "MOSI Only",

            "MOSI + MISO",

            "Back"

        ]

    )




    if mode=="MOSI Only":


        mosi=get_input(

            "MOSI INPUT",

            "Paste MOSI SPI transaction"

        )



        result=run_mosi_decode(

            interface,

            mosi

        )



        viewer(

            "MOSI Decode Result",

            result

        )






    elif mode=="MOSI + MISO":



        mosi=get_input(

            "MOSI INPUT",

            "Paste MOSI bytes"

        )


        miso=get_input(

            "MISO INPUT",

            "Paste MISO bytes"

        )



        result=run_transaction_decode(

            interface,

            mosi,

            miso

        )




        viewer(

            "Transaction Decode Result",

            result

        )


# ======================================================
# CSV ANALYZER
# ======================================================


def csv_menu():


    csv_path = select_file()



    if not csv_path:


        return




    while True:


        choice = menu(

            "BOOT CSV ANALYZER",

            [
                "Generate Clean SPI Transactions",

                "Generate Decoded Transactions",

                "TPM Command Summary",

                "PCR Extend Summary",

                "Decode Transaction By Index",

                "Back"
            ],

            f"""

Loaded File:

{csv_path}

"""

        )






        if choice=="Generate Clean SPI Transactions":


            result = generate_clean_transactions(

                csv_path

            )



            viewer(

                "Clean Transactions",

                result

            )







        elif choice=="Generate Decoded Transactions":


            result = generate_decoded_transactions(

                csv_path

            )



            viewer(

                "Decoded Transactions",

                result

            )








        elif choice=="TPM Command Summary":
        
        
            result,file = generate_command_summary(
            
                csv_path
        
            )
        
        
            viewer(
            
                "TPM Command Summary",
        
                result,
        
                file
        
            )








        elif choice=="PCR Extend Summary":
        
        
            result,file = generate_pcr_summary(
            
                csv_path
        
            )
        
        
            viewer(
            
                "PCR Extend Summary",
        
                result,
        
                file
        
            )



        elif choice=="Decode Transaction By Index":


            index = get_input(

                "TRANSACTION INDEX",

                "Enter transaction index"

            )



            result = decode_index(

                index,

                "FIFO"

            )



            viewer(

                "Transaction Decode",

                result

            )



        elif choice=="Back":


            return







if __name__=="__main__":


    main()