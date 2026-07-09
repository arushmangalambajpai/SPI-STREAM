"""
Cross-platform CSV selector
"""


from tkinter import Tk
from tkinter import filedialog





def select_csv():


    root=Tk()


    root.withdraw()



    root.attributes(

        "-topmost",

        True

    )



    path=filedialog.askopenfilename(

        title="Select SPI Capture CSV",

        filetypes=[

            (

                "CSV Files",

                "*.csv"

            ),

            (

                "All Files",

                "*.*"

            )

        ]

    )



    root.destroy()



    if path=="":

        return None



    return path