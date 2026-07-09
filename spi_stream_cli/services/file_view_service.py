"""
SPI-STREAM File Viewer Service

Supports:
    CSV
    TXT

View generated files inside application.
Open using system apps.
"""


import os
import platform
import subprocess





def preview_file(file):


    if not os.path.exists(file):

        return "File not found"



    with open(

        file,

        "r",

        encoding="utf-8",

        errors="ignore"

    ) as f:


        return f.read()







def open_file(file):


    if platform.system()=="Windows":


        os.startfile(file)



    elif platform.system()=="Darwin":


        subprocess.call(

            [

                "open",

                file

            ]

        )



    else:


        subprocess.call(

            [

                "xdg-open",

                file

            ]

        )