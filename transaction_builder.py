"""
transaction_builder.py

Input:
    boot_seq_csv.csv

Output:
    clean_spi_transactions.csv


Function:
    Raw SPI CSV
        |
        v
    Complete clean SPI transactions


Fixes:
    1. DATA_FIFO READ response fragmentation
    2. DATA_FIFO WRITE TPM header corruption

Does NOT decode TPM.
"""


import csv
import os
import sys



# ==========================================================
# Existing SPI decoder
# ==========================================================


sys.path.append(
    os.path.join(
        os.getcwd(),
        "spi_stream"
    )
)


from spi_header_decoder import convert_spi_to_stream_arr





OUTPUT_FILE="clean_spi_transactions.csv"



# ==========================================================
# Helpers
# ==========================================================


def clean_byte(x):

    if x is None:
        return None


    x=x.strip()


    if x=="":
        return None


    return (
        x.replace("0x","")
        .replace("0X","")
        .upper()
        .zfill(2)
    )





def to_int(data):

    return [
        int(x,16)
        for x in data
    ]





def to_hex(data):

    return [
        f"{x:02X}"
        for x in data
    ]





# ==========================================================
# TPM helpers
# ==========================================================


TPM_TAGS=[

    [0x80,0x01],

    [0x80,0x02],

    [0xC0,0x01],

    [0xC0,0x02]

]




def valid_tpm_packet(data):


    if len(data)<10:

        return False


    if data[:2] not in TPM_TAGS:

        return False


    size=int.from_bytes(

        bytes(data[2:6]),

        "big"

    )


    if size < 10:

        return False


    # EXACT TPM command size required

    if size != len(data):

        return False


    return True





# ==========================================================
# NEW FINAL FIFO COMMAND ERROR DETECTOR + FIX
# ==========================================================


def repair_fifo_command(data):


    """
    Detect same failure decode_tpm_command sees.

    TPM header:

    TAG       0-1
    SIZE      2-5
    CMD_CODE  6-9


    Fix ONLY:

        SIZE[0]
        CMD_CODE[0]


    Example:

    BAD:

    80 01 80 00 00 0F 80 00 01 E3


    GOOD:

    80 01 00 00 00 0F 00 00 01 E3
    """



    # already okay

    if valid_tpm_packet(data):

        return data



    if len(data)<10:

        return data



    # must actually look like TPM command

    if data[:2] not in TPM_TAGS:

        return data




    fixed=data.copy()



    # read exactly like tpm_command_decoder.py


    size=int.from_bytes(

        bytes(data[2:6]),

        "big"

    )



    cmd=int.from_bytes(

        bytes(data[6:10]),

        "big"

    )




    # corrupted MSB

    if size & 0x80000000:


        fixed[2]=0x00




    if cmd & 0x80000000:


        fixed[6]=0x00





    return fixed






# ==========================================================
# MISO response finder
# ==========================================================


def find_tpm_response(data):


    for i in range(len(data)-6):


        if data[i:i+2] in TPM_TAGS:


            size=int.from_bytes(

                bytes(data[i+2:i+6]),

                "big"

            )



            if 10 <= size < 4096:


                return (

                    data[i:],

                    size

                )



    return None,None

# ==========================================================
# TPM command finder
# ==========================================================


def find_tpm_command(data):


    for i in range(len(data)-9):


        if data[i:i+2] in TPM_TAGS:


            candidate = data[i:]


            # fix wait byte corruption first

            candidate = repair_fifo_command(

                candidate

            )



            if len(candidate) < 10:

                continue




            size = int.from_bytes(

                bytes(

                    candidate[2:6]

                ),

                "big"

            )



            if size >= 10:


                return (

                    candidate,

                    size

                )



    return None,None





# ==========================================================
# CSV transaction builder
# ==========================================================


def build_transactions(input_file):


    transactions=[]


    current=None




    with open(

        input_file,

        newline=""

    ) as f:



        reader=csv.DictReader(f)




        for row in reader:



            idx=row["Index"].strip()



            if idx:



                if current:


                    transactions.append(

                        current

                    )



                current={

                    "index":idx,

                    "mosi":[],

                    "miso":[]

                }



            if current is None:

                continue




            mosi=clean_byte(

                row.get("MOSI")

            )


            miso=clean_byte(

                row.get("MISO")

            )




            if mosi:

                current["mosi"].append(mosi)




            if miso:

                current["miso"].append(miso)





        if current:


            transactions.append(

                current

            )




    return transactions






# ==========================================================
# PROCESS TRANSACTIONS
# ==========================================================

# ==========================================================
# PROCESS TRANSACTIONS
# ==========================================================


def process(transactions):


    output=[]


    # ------------------------------
    # MISO response accumulator
    # ------------------------------

    response_buffer=[]

    response_size=None

    response_tx=None



    # ------------------------------
    # MOSI command accumulator
    # ------------------------------

    command_buffer=[]

    command_size=None

    command_tx=None





    for t in transactions:



        try:


            (

                interface,

                op_header,

                operation,

                byte_length,

                locality,

                register_addr,

                payload


            ) = convert_spi_to_stream_arr(

                "FIFO",

                " ".join(t["mosi"])

            )



        except:


            output.append(t)

            continue






        # DATA_FIFO only


        try:

            addr=int(register_addr,16)

        except:

            addr=-1



        # ==================================================
        # FINAL FIFO COMMAND BYPASS
        #
        # Some TPM commands appear on MOSI even when
        # SPI header decode/register logic is misleading.
        #
        # Detect TPM structure directly:
        #
        # SPI_HEADER(4) | TPM_COMMAND
        #
        # Repair before using TPM size.
        # ==================================================


        raw_mosi_payload = to_int(

            t["mosi"][4:]

        )



        force_fifo_command = False




        if (

            len(raw_mosi_payload) >= 10

            and

            raw_mosi_payload[:2] in TPM_TAGS

        ):


                raw_mosi_payload = to_int(
                
                    t["mosi"][4:]

                )


                force_fifo_command=False



                cmd,size=find_tpm_command(
                
                    raw_mosi_payload

                )



                if cmd is not None:
                
                
                    operation="WRITE"


                    payload=to_hex(
                    
                        cmd

                    )


                    force_fifo_command=True





        # ==================================================
        # Ignore non FIFO registers
        #
        # Unless bypass detected TPM command above
        # ==================================================


        if (

            not force_fifo_command

            and

            not (0x024 <= addr <= 0x027)

        ):


            output.append(t)


            continue



        # ==================================================
        # FIFO WRITE COMMAND
        # ==================================================


        if operation=="WRITE":



            #
            # Use raw MOSI payload, not SPI decoded payload.
            #
            # TPM command size is authoritative.
            # SPI byte count can miss wait/turnaround bytes.
            #

            data=to_int(

                t["mosi"][4:]

            )




            # repair TPM header corruption


            data=repair_fifo_command(

                data

            )







            # complete command


            if valid_tpm_packet(data):


                t["mosi"]=(

                    t["mosi"][:4]

                    +

                    to_hex(data)

                )



                output.append(t)



                continue









            # fragmented command start


            if command_size is None:





                if (
                
                    len(data)>=2

                    and

                    data[:2] in TPM_TAGS

                ):


                    # repair immediately when command starts

                    data = repair_fifo_command(data)


                    command_buffer=data.copy()

                    command_tx=t



                    if len(command_buffer)>=6:
                    
                    
                        command_size=int.from_bytes(
                        
                            bytes(
                            
                                command_buffer[2:6]

                            ),

                            "big"

                        )





                else:



                    # orphan FIFO byte
                    # not a TPM transaction


                    continue






            else:
            
            
                # -----------------------------------------
                # Safety:
                #
                # Existing command incomplete,
                # but new FIFO write begins another TPM cmd.
                #
                # Do not merge two TPM commands.
                # -----------------------------------------
            
            
                if (
                
                    len(data) >= 10
            
                    and
            
                    data[:2] in TPM_TAGS
            
                ):
            
            
                    # discard broken accumulator
            
                    command_buffer = data.copy()
            
                    command_tx = t
            
            
                    command_size = int.from_bytes(
                    
                        bytes(
                        
                            command_buffer[2:6]
            
                        ),
            
                        "big"
            
                    )
            
            
                else:
                
                
                    command_buffer.extend(
                    
                        data
            
                    )
            
            
            
            



            # command completed


            if (

                command_size is not None

                and

                len(command_buffer)>=command_size

            ):



                final_cmd=command_buffer[:command_size]



                final_cmd=repair_fifo_command(

                    final_cmd

                )




                command_tx["mosi"]=(

                    command_tx["mosi"][:4]

                    +

                    to_hex(final_cmd)

                )




                output.append(

                    command_tx

                )






                command_buffer=[]

                command_size=None

                command_tx=None










        # ==================================================
        # FIFO READ RESPONSE
        #
        # unchanged
        # ==================================================


        elif operation=="READ":




            data=to_int(

                t["miso"][4:]

            )






            if response_size:



                response_buffer.extend(

                    data

                )





            else:




                start,size=find_tpm_response(

                    data

                )




                if start is None:


                    continue






                response_buffer=start

                response_size=size

                response_tx=t








            if len(response_buffer)>=response_size:




                response_tx["miso"]=(

                    response_tx["miso"][:4]

                    +

                    to_hex(

                        response_buffer[:response_size]

                    )

                )






                output.append(

                    response_tx

                )






                response_buffer=[]

                response_size=None

                response_tx=None







    return output
# ==========================================================
# SAVE
# ==========================================================


def save(data):


    with open(

        OUTPUT_FILE,

        "w",

        newline=""

    ) as f:



        writer=csv.writer(f)



        writer.writerow(

            [

                "Index",

                "Length",

                "MOSI",

                "MISO"

            ]

        )




        for t in data:



            writer.writerow(

                [

                    t["index"],

                    len(t["mosi"]),

                    " ".join(t["mosi"]),

                    " ".join(t["miso"])

                ]

            )







# ==========================================================
# MAIN
# ==========================================================


def main(input_file):


    raw=build_transactions(input_file)


    clean=process(raw)


    save(clean)




    print("="*50)

    print("TRANSACTION BUILDER COMPLETE")

    print("="*50)


    print("Input :",len(raw))

    print("Output:",len(clean))

    print("Saved :",OUTPUT_FILE)






if __name__=="__main__":

    main("rpi_boot_csv.csv")