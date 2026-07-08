"""
SPI-STREAM Object Structures

This file defines the internal objects used by the decoder.

No decoding logic should exist here.

Flow:

SPI bytes
    |
    v
Register Decode
    |
    +--> MOSI_REG / MISO_REG

TPM DATA FIFO / CRB BUFFER
    |
    +--> MOSI_TPM / MISO_TPM
"""


# ==========================================================
# BASE REGISTER OBJECT
# ==========================================================


class REG_BASE:

    def __init__(
        self,
        reg_type,
        operation_type,
        byte_length,
        locality,
        register_addr,
        reg_name
    ):

        # FIFO / CRB
        self.reg_type = reg_type


        # READ / WRITE
        self.operation_type = operation_type


        # SPI transfer length
        self.byte_length = byte_length


        # TPM locality
        self.locality = locality


        # register address
        self.register_addr = register_addr


        # TPM_STS, TPM_ACCESS, etc.
        self.reg_name = reg_name



    def show(self):

        print("\n========== REGISTER ==========")

        print("Interface      :", self.reg_type)
        print("Operation      :", self.operation_type)
        print("Byte Length    :", self.byte_length)
        print("Locality       :", self.locality)
        print("Register Addr  :", self.register_addr)
        print("Register Name  :", self.reg_name)



# ==========================================================
# MOSI REGISTER OBJECT
# ==========================================================


class MOSI_REG(REG_BASE):

    def __init__(
        self,
        reg_type,
        operation_type,
        byte_length,
        locality,
        register_addr,
        reg_name,
        reg_payload,
        reg_payload_decoded_op
    ):

        super().__init__(
            reg_type,
            operation_type,
            byte_length,
            locality,
            register_addr,
            reg_name
        )


        self.reg_payload = reg_payload


        # contains:
        #
        # {
        #   "description":"",
        #   "summary":""
        # }
        #
        self.reg_payload_decoded_op = reg_payload_decoded_op



    def show(self):

        super().show()

        print("Payload        :", self.reg_payload)

        print("\nDescription:")
        print(
            self.reg_payload_decoded_op.get(
                "description",
                ""
            )
        )

        print("\nSummary:")
        print(
            self.reg_payload_decoded_op.get(
                "summary",
                ""
            )
        )



# ==========================================================
# MISO REGISTER OBJECT
# ==========================================================


class MISO_REG(REG_BASE):

    def __init__(
        self,
        reg_type,
        operation_type,
        byte_length,
        locality,
        register_addr,
        reg_name,
        response_payload,
        response_payload_decoded_op
    ):

        super().__init__(
            reg_type,
            operation_type,
            byte_length,
            locality,
            register_addr,
            reg_name
        )


        self.response_payload = response_payload


        self.response_payload_decoded_op = (
            response_payload_decoded_op
        )



    def show(self):

        super().show()

        print(
            "Response Payload:",
            self.response_payload
        )

        print("\nDescription:")

        print(
            self.response_payload_decoded_op.get(
                "description",
                ""
            )
        )


        print("\nSummary:")

        print(
            self.response_payload_decoded_op.get(
                "summary",
                ""
            )
        )



# ==========================================================
# MOSI TPM COMMAND OBJECT
# ==========================================================


class MOSI_TPM(MOSI_REG):

    def __init__(
        self,
        *args,

        tag=None,
        cmd_size=None,
        cmd_code=None,
        cmd_name=None,
        tpm_payload_decoded_op=None
    ):


        super().__init__(*args)


        self.tag = tag

        self.cmd_size = cmd_size

        self.cmd_code = cmd_code

        self.cmd_name = cmd_name


        # tpmstream tree output

        self.tpm_payload_decoded_op = (
            tpm_payload_decoded_op
        )



    def show(self):

        super().show()

        print("\n========== TPM COMMAND ==========")

        print("TAG       :", self.tag)

        print("SIZE      :", self.cmd_size)

        print("CODE      :", self.cmd_code)

        print("COMMAND   :", self.cmd_name)

        print("\nTPM Tree:")

        print(self.tpm_payload_decoded_op)



# ==========================================================
# MISO TPM RESPONSE OBJECT
# ==========================================================


class MISO_TPM(MISO_REG):

    def __init__(
        self,
        *args,

        tag=None,
        response_size=None,
        response_code=None,
        response_name=None,
        tpm_response_decoded_op=None
    ):


        super().__init__(*args)


        self.tag = tag

        self.response_size = response_size

        self.response_code = response_code

        self.response_name = response_name


        self.tpm_response_decoded_op = (
            tpm_response_decoded_op
        )



    def show(self):

        super().show()

        print("\n========== TPM RESPONSE ==========")

        print("TAG          :", self.tag)

        print("SIZE         :", self.response_size)

        print("CODE         :", self.response_code)

        print("RESPONSE     :", self.response_name)

        print("\nTPM Tree:")

        print(self.tpm_response_decoded_op)