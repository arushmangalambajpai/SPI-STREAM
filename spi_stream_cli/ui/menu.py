"""
SPI-STREAM Menu UI

Full screen command center.
"""


from rich.console import Console
from rich.panel import Panel
from rich.align import Align

import readchar



console = Console()





def menu(title, options, subtitle=""):


    index=0



    while True:


        console.clear()


        text=""


        if subtitle:


            text += subtitle + "\n\n"



        for i,opt in enumerate(options):


            if i==index:


                text += "   ▸ " + opt + "\n"


            else:


                text += "     " + opt + "\n"





        console.print(

            Panel(

                Align.center(text),

                title=title,

                expand=True

            )

        )



        key=readchar.readkey()



        if key==readchar.key.UP:


            index=(index-1)%len(options)



        elif key==readchar.key.DOWN:


            index=(index+1)%len(options)




        elif key==readchar.key.ENTER:


            return options[index]