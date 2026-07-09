"""
Cross platform file picker
"""


from tkinter import Tk
from tkinter import filedialog




def select_file():


    root = Tk()


    root.withdraw()


    root.attributes(

        "-topmost",

        True

    )



    file = filedialog.askopenfilename(

        title="Select SPI CSV File",

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



    return file