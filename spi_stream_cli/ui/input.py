"""
Input screens
"""


from rich.console import Console
from rich.panel import Panel


console=Console()





def get_input(title,message):


    console.clear()



    console.print(

        Panel(

            message,

            title=title

        )

    )



    return input(

        "\n> "

    )