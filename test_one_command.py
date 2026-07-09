import os
import sys

sys.path.append(
    os.path.join(
        os.getcwd(),
        "spi_stream"
    )
)


from tpm_command_decoder import decode_tpm_command


cmd = """
80 01 00 00 00 16
00 00 01 7B
00 00 00 06
00 00 01 12
00 00 00 01
"""


cmd = cmd.split()


print(
    decode_tpm_command(cmd)
)