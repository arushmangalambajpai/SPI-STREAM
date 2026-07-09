"""
SPI-STREAM CLI Decode Service
"""


import io
import contextlib


from spi_stream.decode_spi import (

    decode_mosi,

    decode_transaction

)





def capture_show(obj):


    buffer = io.StringIO()


    with contextlib.redirect_stdout(

        buffer

    ):


        if obj:


            obj.show()


    return buffer.getvalue()








def run_mosi_decode(

    interface,

    mosi

):


    obj = decode_mosi(

        mosi,

        interface

    )


    return capture_show(

        obj

    )









def run_transaction_decode(

    interface,

    mosi,

    miso

):


    mosi_obj,miso_obj = decode_transaction(

        mosi,

        miso,

        interface

    )



    output = ""


    output += capture_show(

        mosi_obj

    )



    if miso_obj:


        output += "\n\n"


        output += capture_show(

            miso_obj

        )



    return output