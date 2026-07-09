"""
SPI-STREAM terminal layout
"""


from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live


console = Console()



def create_layout():


    layout = Layout()


    layout.split_column(

        Layout(
            name="header",
            size=5
        ),


        Layout(
            name="body"
        )

    )


    layout["body"].split_row(

        Layout(
            name="commands",
            ratio=1
        ),


        Layout(
            name="output",
            ratio=2
        )

    )


    return layout





def show_screen(

    command_text,

    output_text

):


    layout=create_layout()



    layout["header"].update(

        Panel(

            """
SPI-STREAM

Made By @arushmangalambajpai
Based on TPM Specifications & tpmstream
""",

            border_style="green"

        )

    )



    layout["commands"].update(

        Panel(

            command_text,

            title="COMMAND",

            border_style="green"

        )

    )



    layout["output"].update(

        Panel(

            output_text,

            title="OUTPUT",

            border_style="green"

        )

    )



    console.clear()


    console.print(

        layout

    )