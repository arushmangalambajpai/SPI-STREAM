"""
SPI-STREAM Launcher

Starts CLI application in separate window.
Works Windows/Linux.
"""


import os
import sys
import subprocess
import platform





def launch_windows():


    python_exe=sys.executable



    command=(

        'start "SPI-STREAM" '

        '/MAX '

        'cmd /k '

        f'"{python_exe} -m spi_stream_cli.app"'

    )



    subprocess.Popen(

        command,

        shell=True

    )








def launch_linux():


    python_exe=sys.executable



    terminals=[


        [

            "gnome-terminal",

            "--maximize",

            "--",

            python_exe,

            "-m",

            "spi_stream_cli.app"

        ],



        [

            "konsole",

            "--fullscreen",

            "-e",

            python_exe,

            "-m",

            "spi_stream_cli.app"

        ],



        [

            "xterm",

            "-maximized",

            "-e",

            python_exe,

            "-m",

            "spi_stream_cli.app"

        ]

    ]




    for cmd in terminals:


        try:


            subprocess.Popen(cmd)

            return



        except:


            pass





    print(

        "No supported terminal found."

    )










if __name__=="__main__":



    if platform.system()=="Windows":


        launch_windows()



    else:


        launch_linux()