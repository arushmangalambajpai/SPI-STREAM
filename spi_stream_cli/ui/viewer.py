"""
SPI-STREAM Output Viewer

Large output friendly.
"""


from rich.console import Console
from rich.panel import Panel
from rich.align import Align

import readchar
import os


from spi_stream_cli.services.file_view_service import (

    preview_file,

    open_file

)
console=Console()





def save_output(title,text):


    os.makedirs(
        "output",
        exist_ok=True
    )


    path=os.path.join(

        "output",

        title.replace(
            " ",
            "_"
        )

        +

        ".txt"

    )


    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(text)



    return path







def viewer(title,text, file=None):


    while True:


        console.clear()



        console.print(

            Panel(

                Align.center(title),

                expand=True

            )

        )



        # IMPORTANT
        # raw print keeps TPM tree spacing

        print(text)




        print(
            "\n"
            +
            "="*80
        )


        if file:


            print(

                "[B] Back   [S] Save Text   [V] View File   [O] Open File"

            )


        else:


            print(

                "[B] Back   [S] Save Text"

            )




        key=readchar.readkey()



        if key.lower()=="b":


            return



        elif key.lower()=="s":


            path=save_output(

                title,

                text

            )



            print(

                "\nSaved:",

                path

            )


            readchar.readkey()
        elif (
        
            file

            and

            key.lower()=="v"

        ):


            console.clear()


            print(
            
                preview_file(
                
                    file
            
                )
            
            )


            input(
            
                "\nPress Enter..."

            )





        elif (
        
            file

            and

            key.lower()=="o"

        ):


            open_file(
            
                file

            )