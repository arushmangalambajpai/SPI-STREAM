"""
SPI-STREAM CSV Service

Connects CLI application with
existing SPI-STREAM utilities.

No decoding logic here.
"""


import os
import sys
import io
import shutil
import contextlib



# ======================================================
# PATH SETUP
# ======================================================


ROOT_DIR = os.path.abspath(

    os.path.join(

        os.path.dirname(__file__),

        "..",

        ".."

    )

)



PATHS = [

    ROOT_DIR,

    os.path.join(

        ROOT_DIR,

        "spi_stream"

    ),

    os.path.join(

        ROOT_DIR,

        "utilities"

    )

]




for path in PATHS:


    if path not in sys.path:


        sys.path.append(

            path

        )







# ======================================================
# IMPORT EXISTING TOOLS
# ======================================================


import transaction_builder


import transaction_csv_decoder


import tpm_command_summary


import pcr_extend_summaries







OUTPUT_DIR=os.path.join(

    ROOT_DIR,

    "output"

)









# ======================================================
# HELPERS
# ======================================================


def ensure_output():


    os.makedirs(

        OUTPUT_DIR,

        exist_ok=True

    )


def save_text_file(

    filename,

    text

):


    ensure_output()



    path=os.path.join(

        OUTPUT_DIR,

        filename

    )



    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:


        f.write(text)



    return path




def capture_output(

    function

):


    buffer=io.StringIO()



    with contextlib.redirect_stdout(

        buffer

    ):


        function()




    return buffer.getvalue()







def copy_if_exists(

    filename

):


    src=os.path.join(

        ROOT_DIR,

        filename

    )



    dst=os.path.join(

        OUTPUT_DIR,

        filename

    )




    if os.path.exists(

        src

    ):


        shutil.copy(

            src,

            dst

        )








# ======================================================
# CLEAN TRANSACTIONS
# ======================================================

def generate_clean_transactions(csv_path):


    ensure_output()



    transaction_builder.INPUT_FILE = csv_path



    result = capture_output(

        transaction_builder.main

    )



    file = os.path.join(

        ROOT_DIR,

        "clean_spi_transactions.csv"

    )



    return result,file









# ======================================================
# DECODED TRANSACTIONS
# ======================================================

def generate_decoded_transactions(csv_path):


    ensure_output()



    generate_clean_transactions(

        csv_path

    )



    result = capture_output(

        transaction_csv_decoder.main

    )



    file = os.path.join(

        ROOT_DIR,

        "decoded_transactions.csv"

    )



    return result,file

# ======================================================
# COMMAND SUMMARY
# ======================================================

def generate_command_summary(csv_path):


    generate_decoded_transactions(

        csv_path

    )



    result = capture_output(

        tpm_command_summary.main

    )



    file = os.path.join(

        ROOT_DIR,

        "tpm_command_summary.txt"

    )



    return result,file

    











# ======================================================
# PCR EXTEND SUMMARY
# ======================================================

def generate_pcr_summary(csv_path):


    generate_decoded_transactions(

        csv_path

    )



    result = capture_output(

        pcr_extend_summaries.main

    )



    file = os.path.join(

        ROOT_DIR,

        "pcr_extend_summary.txt"

    )



    return result,file