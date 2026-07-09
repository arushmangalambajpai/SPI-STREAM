"""
Output manager
"""


import os

from spi_stream_cli.config import OUTPUT_FOLDER





def save_output(filename,text):


    if not os.path.exists(

        OUTPUT_FOLDER

    ):


        os.mkdir(

            OUTPUT_FOLDER

        )



    path=os.path.join(

        OUTPUT_FOLDER,

        filename

    )



    with open(

        path,

        "w"

    ) as f:


        f.write(

            text

        )



    return path