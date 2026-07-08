"""
TPM Register Payload Decoder

Input:

register name
payload bytes
operation READ/WRITE

Output:

{
    "description": "...",
    "summary": "..."
}


Description:
    Direct TPM specification bit decoding

Summary:
    TPM behaviour/state interpretation


No TPM command decoding happens here.
"""


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================


def payload_to_int(payload):

    """
    Accept:

    ["00","00","00","90"]

    or

    "00 00 00 90"

    Convert to integer.
    """


    if isinstance(payload, list):

        hex_string = "".join(payload)


    else:

        hex_string = payload.replace(
            " ",
            ""
        )


    if hex_string == "":

        return 0


    return int(
        hex_string,
        16
    )



def get_bit(value, bit):


    return (
        value >> bit
    ) & 1



def get_bits(
        value,
        high,
        low
    ):


    mask = (
        (1 << (high-low+1))
        -
        1
    )


    return (
        value >> low
    ) & mask



def make_output(
        description,
        summary
    ):


    return {

        "description":
            description.strip(),


        "summary":
            summary.strip()

    }



# ==========================================================
# FIFO : TPM_ACCESS
# ==========================================================


def decode_TPM_ACCESS(
        payload,
        operation
    ):


    value = payload_to_int(
        payload
    )


    description = ""

    summary = ""



    if operation == "READ":


        valid = get_bit(value,7)

        active = get_bit(value,5)

        seized = get_bit(value,4)

        pending = get_bit(value,2)

        request = get_bit(value,1)

        establish = get_bit(value,0)



        description += f"""

[7] tpmRegValidSts = {valid}
{ 'Register contents are valid'
if valid else
'Register contents are not valid' }


[5] activeLocality = {active}
{ 'This locality controls TPM'
if active else
'This locality is not active' }


[4] beenSeized = {seized}
{ 'Control was taken by higher locality'
if seized else
'Normal locality operation' }


[2] pendingRequest = {pending}
{ 'Another locality requested TPM'
if pending else
'No other locality request' }


[1] requestUse = {request}
{ 'Locality requesting TPM usage'
if request else
'No active request' }


[0] tpmEstablishment = {establish}
"""



        if valid and active:

            summary += """

TPM locality negotiation completed.

Current locality owns TPM and can issue commands.
"""


        if seized:

            summary += """

A higher priority locality has taken TPM control.
"""



    elif operation == "WRITE":


        if get_bit(value,5):

            description += """

[5] activeLocality = 1
Relinquish locality control.
"""

            summary += """

Host released TPM locality ownership.
"""


        if get_bit(value,3):

            description += """

[3] seize = 1
Request higher priority TPM control.
"""

            summary += """

Host attempted locality seizure.
"""


        if get_bit(value,1):

            description += """

[1] requestUse = 1
Request locality access.
"""

            summary += """

Host requested TPM locality ownership.
"""



    return make_output(
        description,
        summary
    )



# ==========================================================
# FIFO : TPM_INT_ENABLE
# ==========================================================


def decode_TPM_INT_ENABLE(
        payload,
        operation
    ):


    value = payload_to_int(
        payload
    )


    description = ""

    summary = ""



    global_enable = get_bit(value,31)


    command = get_bit(value,3)

    locality = get_bit(value,2)

    sts = get_bit(value,1)

    data = get_bit(value,0)



    description += f"""

[31] globalIntEnable = {global_enable}

[3] commandReadyIntEnable = {command}

[2] localityChangeIntEnable = {locality}

[1] stsValidIntEnable = {sts}

[0] dataAvailIntEnable = {data}

"""



    if global_enable:

        summary += """

TPM interrupt generation is globally enabled.
"""


        if data:

            summary += """

TPM will interrupt host when response data becomes available.
"""

    else:

        summary += """

TPM interrupts are globally disabled.
"""



    return make_output(
        description,
        summary
    )



# ==========================================================
# FIFO : TPM_INT_VECTOR
# ==========================================================


def decode_TPM_INT_VECTOR(
        payload,
        operation
    ):


    value = payload_to_int(
        payload
    )


    return make_output(

        f"""
[7:0] SIRQVector = {value}

TPM interrupt vector value.
""",

        """
TPM interrupt routing/vector configuration accessed.
"""

    )



# ==========================================================
# FIFO : TPM_INT_STATUS
# ==========================================================


def decode_TPM_INT_STATUS(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = ""

    summary = ""



    cmd = get_bit(value,7)

    loc = get_bit(value,2)

    sts = get_bit(value,1)

    data = get_bit(value,0)



    description += f"""

[7] commandReadyIntOccurred = {cmd}

[2] localityChangeIntOccurred = {loc}

[1] stsValidIntOccurred = {sts}

[0] dataAvailIntOccurred = {data}

"""


    if operation == "READ":


        if data:

            summary += """

TPM generated interrupt because response data became available.
"""


        if cmd:

            summary += """

TPM command ready state transition occurred.
"""


    else:


        summary += """

Host cleared selected TPM interrupt status flags.
"""



    return make_output(
        description,
        summary
    )
# ==========================================================
# FIFO : TPM_INTF_CAPABILITY
# ==========================================================


def decode_TPM_INTF_CAPABILITY(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = ""

    summary = ""



    version = get_bits(value,30,28)

    transfer = get_bits(value,10,9)

    burst_static = get_bit(value,8)



    description += f"""

[30:28] InterfaceVersion = {version}

[10:9] DataTransferSizeSupport = {transfer}

[8] BurstCountStatic = {burst_static}

[7] CommandReadyIntSupport = {get_bit(value,7)}

[6] InterruptEdgeFalling = {get_bit(value,6)}

[5] InterruptEdgeRising = {get_bit(value,5)}

[4] InterruptLevelLow = {get_bit(value,4)}

[3] InterruptLevelHigh = {get_bit(value,3)}

[2] LocalityChangeIntSupport = {get_bit(value,2)}

[1] StsValidIntSupport = {get_bit(value,1)}

[0] DataAvailIntSupport = {get_bit(value,0)}

"""


    if version == 3:

        summary += """

TPM supports FIFO interface communication.
"""


    transfer_text = {

        0:
        "Legacy transfer size only supported",

        1:
        "Maximum 8 byte transfer supported",

        2:
        "Maximum 32 byte transfer supported",

        3:
        "Maximum 64 byte transfer supported"

    }


    summary += transfer_text.get(
        transfer,
        ""
    )


    return make_output(
        description,
        summary
    )



# ==========================================================
# FIFO : TPM_STS
# ==========================================================


def decode_TPM_STS(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = ""

    summary = ""



    if operation == "READ":


        family = get_bits(value,27,26)

        burst = get_bits(value,23,8)

        valid = get_bit(value,7)

        ready = get_bit(value,6)

        data = get_bit(value,4)

        expect = get_bit(value,3)

        selftest = get_bit(value,2)



        description += f"""

[27:26] tpmFamily = {family}

[23:8] burstCount = {burst}

[7] stsValid = {valid}

[6] commandReady = {ready}

[4] dataAvail = {data}

[3] expect = {expect}

[2] selfTestDone = {selftest}

"""


        if valid and ready:

            summary += """

TPM is ready to receive a command.
"""


        if valid and expect:

            summary += """

TPM expects more command bytes.
Continue writing FIFO data.
"""


        if valid and data:

            summary += """

TPM command execution completed.

Response bytes are available in FIFO.
"""



    else:


        if get_bit(value,25):

            description += """

[25] resetEstablishmentBit = 1
"""

            summary += """

Host reset TPM establishment flag.
"""



        if get_bit(value,24):

            description += """

[24] commandCancel = 1
"""

            summary += """

Host cancelled current TPM command.
"""



        if get_bit(value,6):

            description += """

[6] commandReady = 1
"""

            summary += """

Host prepared FIFO for a new TPM command.
"""



        if get_bit(value,5):

            description += """

[5] tpmGo = 1
"""

            summary += """

Host started TPM command execution.
"""



        if get_bit(value,1):

            description += """

[1] responseRetry = 1
"""

            summary += """

Host requested TPM response retransmission.
"""



    return make_output(
        description,
        summary
    )



# ==========================================================
# FIFO : TPM_INTERFACE_ID
# ==========================================================


def decode_TPM_INTERFACE_ID(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = ""

    summary = ""



    checksum = get_bits(value,23,22)

    selector = get_bits(value,18,17)

    crb = get_bit(value,14)

    fifo = get_bit(value,13)

    locality = get_bit(value,8)

    version = get_bits(value,7,4)

    interface = get_bits(value,3,0)



    description += f"""

[23:22] CapSPICsum = {checksum}

[18:17] InterfaceSelector = {selector}

[14] CapCRB = {crb}

[13] CapFIFO = {fifo}

[8] CapLocality = {locality}

[7:4] InterfaceVersion = {version}

[3:0] InterfaceType = {interface}

"""


    if fifo and crb:

        summary += """

TPM supports both FIFO and CRB interfaces.
"""


    elif fifo:

        summary += """

TPM supports FIFO interface.
"""


    elif crb:

        summary += """

TPM supports CRB interface.
"""



    return make_output(
        description,
        summary
    )



# ==========================================================
# FIFO : CHECKSUM ENABLE
# ==========================================================


def decode_TPM_DATA_CSUM_ENABLE(
        payload,
        operation
    ):


    enabled = get_bit(
        payload_to_int(payload),
        0
    )


    return make_output(

        f"""

[0] dataCsumEnable = {enabled}

""",

        (
        "TPM checksum calculation enabled."
        if enabled
        else
        "TPM checksum calculation disabled."
        )

    )



# ==========================================================
# FIFO : DATA CHECKSUM
# ==========================================================


def decode_TPM_DATA_CSUM(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    checksum = (
        value & 0xFFFF
    )


    return make_output(

        f"""

[15:0] dataChecksum = {hex(checksum)}

""",

        """

TPM command/response checksum value accessed.

"""

    )



# ==========================================================
# FIFO : DEVICE ID / VENDOR ID
# ==========================================================


def decode_TPM_DID_VID(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    did = get_bits(value,31,16)

    vid = get_bits(value,15,0)



    return make_output(

        f"""

Device ID = {hex(did)}

Vendor ID = {hex(vid)}

""",

        """

TPM vendor and device identification read.

"""

    )



# ==========================================================
# FIFO : REVISION ID
# ==========================================================


def decode_TPM_RID(
        payload,
        operation
    ):


    value = payload_to_int(payload)



    return make_output(

        f"""

Revision ID = {hex(value)}

""",

        """

TPM hardware revision information read.

"""

    )



# ==========================================================
# FIFO : DATA FIFO
# ==========================================================


def decode_TPM_DATA_FIFO(
        payload,
        operation
    ):


    size = len(payload)



    if operation == "WRITE":


        summary = (

        f"""

Host wrote {size} bytes into TPM FIFO.

Possible TPM command stream.

"""

        )


    else:


        summary = (

        f"""

Host read {size} response bytes from TPM FIFO.

Possible TPM response stream.

"""

        )



    return make_output(

        "FIFO byte stream transfer.",

        summary

    )



# ==========================================================
# FIFO : EXTENDED DATA FIFO
# ==========================================================


def decode_TPM_XDATA_FIFO(
        payload,
        operation
    ):


    return make_output(

        "Extended FIFO byte stream transfer.",

        "Extended TPM FIFO transaction occurred."

    )

# ==========================================================
# CRB : TPM_LOC_STATE
# ==========================================================


def decode_TPM_LOC_STATE(payload, operation):


    value = payload_to_int(payload)


    assigned = get_bit(value,8)

    active = get_bit(value,2)

    seized = get_bit(value,1)

    request = get_bit(value,0)


    description = f"""

[8] localityAssigned = {assigned}

[2] activeLocality = {active}

[1] localityBeingSeized = {seized}

[0] localityRequest = {request}

"""


    summary = ""


    if assigned and active:

        summary += """

CRB locality is active.

Current software layer owns TPM access.
"""


    if seized:

        summary += """

Higher priority locality is attempting TPM takeover.
"""


    if request:

        summary += """

TPM locality access request is pending.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : TPM_LOC_CTRL
# ==========================================================


def decode_TPM_LOC_CTRL(payload, operation):


    value = payload_to_int(payload)


    description = ""

    summary = ""


    if get_bit(value,2):

        description += """

[2] seize = 1

Request TPM locality seizure.
"""

        summary += """

Host requested higher priority TPM locality ownership.
"""


    if get_bit(value,1):

        description += """

[1] relinquish = 1

Release active locality.
"""

        summary += """

Host released CRB locality ownership.
"""


    if get_bit(value,0):

        description += """

[0] requestAccess = 1

Request locality access.
"""

        summary += """

Host requested CRB TPM access.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : TPM_LOC_STS
# ==========================================================


def decode_TPM_LOC_STS(payload, operation):


    value = payload_to_int(payload)


    seized = get_bit(value,1)

    granted = get_bit(value,0)


    description = f"""

[1] beenSeized = {seized}

[0] granted = {granted}

"""


    summary = ""


    if granted:

        summary += """

CRB locality access granted.
"""


    if seized:

        summary += """

This locality was seized by higher priority locality.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : TPM_CRB_INTF_ID
# ==========================================================


def decode_TPM_CRB_INTF_ID(payload, operation):


    value = payload_to_int(payload)


    selector = get_bits(value,18,17)

    cap_crb = get_bit(value,14)

    cap_fifo = get_bit(value,13)


    description = f"""

[18:17] InterfaceSelector = {selector}

[14] CapCRB = {cap_crb}

[13] CapFIFO = {cap_fifo}

[3:0] InterfaceType = {get_bits(value,3,0)}

"""


    summary = ""


    if cap_crb:

        summary += """

TPM supports CRB interface.
"""


    if cap_fifo:

        summary += """

TPM also supports FIFO interface.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : CTRL REQUEST
# ==========================================================


def decode_TPM_CRB_CTRL_REQ(payload, operation):


    value = payload_to_int(payload)


    idle = get_bit(value,1)

    ready = get_bit(value,0)


    description = f"""

[1] goIdle = {idle}

[0] cmdReady = {ready}

"""


    summary = ""


    if ready:

        summary += """

Host requested TPM command reception state.

CRB buffer is ready for command transfer.
"""


    if idle:

        summary += """

Host requested TPM idle state.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : CTRL STATUS
# ==========================================================


def decode_TPM_CRB_CTRL_STS(payload, operation):


    value = payload_to_int(payload)


    idle = get_bit(value,1)

    error = get_bit(value,0)


    description = f"""

[1] tpmIdle = {idle}

[0] error = {error}

"""


    summary = ""


    if idle:

        summary += """

TPM is currently idle.
"""


    if error:

        summary += """

TPM reported CRB interface error.
"""


    return make_output(description, summary)



# ==========================================================
# CRB : CANCEL
# ==========================================================


def decode_TPM_CRB_CTRL_CANCEL(payload, operation):


    cancel = get_bit(
        payload_to_int(payload),
        0
    )


    return make_output(

        f"""

[0] cancel = {cancel}

""",

        (
        "Current TPM command cancellation requested."
        if cancel else
        "No TPM command cancellation pending."
        )

    )



# ==========================================================
# CRB : START
# ==========================================================


def decode_TPM_CRB_CTRL_START(payload, operation):


    value = payload_to_int(payload)


    chunk = get_bit(value,2)

    retry = get_bit(value,1)

    start = get_bit(value,0)



    description = f"""

[2] nextChunk = {chunk}

[1] crbRspRetry = {retry}

[0] start = {start}

"""


    summary = ""


    if start:

        summary += """

TPM command execution started using CRB buffer.
"""


    else:

        summary += """

TPM command execution is not active or completed.
"""


    if retry:

        summary += """

Host requested response retry.
"""


    return make_output(description, summary)

# ==========================================================
# CRB : INTERRUPT ENABLE
# ==========================================================


def decode_TPM_CRB_INT_ENABLE(payload, operation):


    value = payload_to_int(payload)


    global_int = get_bit(value,31)

    complete = get_bit(value,1)

    ready = get_bit(value,0)



    description = f"""

[31] globalIntEnable = {global_int}

[1] commandCompleteIntEnable = {complete}

[0] commandReadyIntEnable = {ready}

"""


    summary = ""


    if global_int:

        summary += """

CRB interrupt system is enabled.
"""


    if complete:

        summary += """

TPM will interrupt host after command completion.
"""


    if ready:

        summary += """

TPM will interrupt host when command ready transition occurs.
"""



    return make_output(description, summary)




# ==========================================================
# CRB : INTERRUPT STATUS
# ==========================================================


def decode_TPM_CRB_INT_STS(payload, operation):


    value = payload_to_int(payload)


    complete = get_bit(value,1)

    ready = get_bit(value,0)



    description = f"""

[1] commandCompleteIntOccurred = {complete}

[0] commandReadyIntOccurred = {ready}

"""


    summary = ""


    if operation == "READ":


        if complete:

            summary += """

TPM command execution completion interrupt occurred.
"""


        if ready:

            summary += """

TPM command ready interrupt occurred.
"""


    else:


        summary += """

Host cleared CRB interrupt status flags.
"""



    return make_output(description, summary)




# ==========================================================
# CRB : COMMAND SIZE
# ==========================================================


def decode_TPM_CRB_CTRL_CMD_SIZE(payload, operation):


    size = payload_to_int(payload)



    return make_output(

        f"""

[31:0] commandSize = {size} bytes

""",

        """

CRB command buffer size information accessed.

"""

    )




# ==========================================================
# CRB : COMMAND LOW ADDRESS
# ==========================================================


def decode_TPM_CRB_CTRL_CMD_LADDR(payload, operation):


    addr = payload_to_int(payload)



    return make_output(

        f"""

Command Buffer Lower Address:

{hex(addr)}

""",

        """

Lower physical address of TPM command buffer accessed.

"""

    )




# ==========================================================
# CRB : COMMAND HIGH ADDRESS
# ==========================================================


def decode_TPM_CRB_CTRL_CMD_HADDR(payload, operation):


    addr = payload_to_int(payload)



    return make_output(

        f"""

Command Buffer Upper Address:

{hex(addr)}

""",

        """

Upper physical address of TPM command buffer accessed.

"""

    )





# ==========================================================
# CRB : RESPONSE SIZE
# ==========================================================


def decode_TPM_CRB_CTRL_RSP_SIZE(payload, operation):


    size = payload_to_int(payload)



    return make_output(

        f"""

Response Buffer Size:

{size} bytes

""",

        """

CRB response buffer size information accessed.

"""

    )





# ==========================================================
# CRB : RESPONSE ADDRESS
# ==========================================================


def decode_TPM_CRB_CTRL_RSP_ADDR(payload, operation):


    addr = payload_to_int(payload)



    return make_output(

        f"""

Response Buffer Address:

{hex(addr)}

""",

        """

Physical memory location where TPM writes responses.

"""

    )





# ==========================================================
# CRB : DATA BUFFER
# ==========================================================


def decode_TPM_CRB_DATA_BUFFER(payload, operation):


    size = len(payload)



    if operation == "WRITE":


        summary = f"""

Host wrote {size} bytes into CRB command buffer.

Possible TPM command stream.

"""


    else:


        summary = f"""

Host read {size} bytes from CRB response buffer.

Possible TPM response stream.

"""



    return make_output(

        "CRB TPM byte stream transfer.",

        summary

    )





# ==========================================================
# MAIN WRAPPER FUNCTION
# ==========================================================


def decode_register_payload(
        reg_name,
        payload,
        operation
    ):


    decoder_table = {


        # FIFO

        "TPM_ACCESS":
        decode_TPM_ACCESS,


        "TPM_INT_ENABLE":
        decode_TPM_INT_ENABLE,


        "TPM_INT_VECTOR":
        decode_TPM_INT_VECTOR,


        "TPM_INT_STATUS":
        decode_TPM_INT_STATUS,


        "TPM_INTF_CAPABILITY":
        decode_TPM_INTF_CAPABILITY,


        "TPM_STS":
        decode_TPM_STS,


        "TPM_INTERFACE_ID":
        decode_TPM_INTERFACE_ID,


        "TPM_DATA_CSUM_ENABLE":
        decode_TPM_DATA_CSUM_ENABLE,


        "TPM_DATA_CSUM":
        decode_TPM_DATA_CSUM,


        "TPM_DID_VID":
        decode_TPM_DID_VID,


        "TPM_RID":
        decode_TPM_RID,


        "TPM_DATA_FIFO":
        decode_TPM_DATA_FIFO,


        "TPM_XDATA_FIFO":
        decode_TPM_XDATA_FIFO,



        # CRB


        "TPM_LOC_STATE":
        decode_TPM_LOC_STATE,


        "TPM_LOC_CTRL":
        decode_TPM_LOC_CTRL,


        "TPM_LOC_STS":
        decode_TPM_LOC_STS,


        "TPM_CRB_INTF_ID":
        decode_TPM_CRB_INTF_ID,


        "TPM_CRB_CTRL_REQ":
        decode_TPM_CRB_CTRL_REQ,


        "TPM_CRB_CTRL_STS":
        decode_TPM_CRB_CTRL_STS,


        "TPM_CRB_CTRL_CANCEL":
        decode_TPM_CRB_CTRL_CANCEL,


        "TPM_CRB_CTRL_START":
        decode_TPM_CRB_CTRL_START,


        "TPM_CRB_INT_ENABLE":
        decode_TPM_CRB_INT_ENABLE,


        "TPM_CRB_INT_STS":
        decode_TPM_CRB_INT_STS,


        "TPM_CRB_CTRL_CMD_SIZE":
        decode_TPM_CRB_CTRL_CMD_SIZE,


        "TPM_CRB_CTRL_CMD_LADDR":
        decode_TPM_CRB_CTRL_CMD_LADDR,


        "TPM_CRB_CTRL_CMD_HADDR":
        decode_TPM_CRB_CTRL_CMD_HADDR,


        "TPM_CRB_CTRL_RSP_SIZE":
        decode_TPM_CRB_CTRL_RSP_SIZE,


        "TPM_CRB_CTRL_RSP_ADDR":
        decode_TPM_CRB_CTRL_RSP_ADDR,


        "TPM_CRB_DATA_BUFFER":
        decode_TPM_CRB_DATA_BUFFER

    }



    if reg_name in decoder_table:


        return decoder_table[reg_name](
            payload,
            operation
        )


    return make_output(

        "No decoder available.",

        "Unknown or reserved register."

    )

# ==========================================================
# FULL SELF TEST
# ==========================================================


if __name__ == "__main__":


    print("\nTPM REGISTER PAYLOAD DECODER TEST\n")


    tests = [


        ("TPM_ACCESS","A2"),

        ("TPM_INT_ENABLE","80000009"),

        ("TPM_INT_VECTOR","05"),

        ("TPM_INT_STATUS","83"),

        ("TPM_INTF_CAPABILITY","300003FF"),

        ("TPM_STS","00000090"),

        ("TPM_INTERFACE_ID","00006100"),

        ("TPM_DATA_CSUM_ENABLE","01"),

        ("TPM_DATA_CSUM","1234"),

        ("TPM_DID_VID","001B15D1"),

        ("TPM_RID","22"),

        ("TPM_DATA_FIFO",["80","01","00"]),

        ("TPM_XDATA_FIFO",["80","02"]),



        ("TPM_LOC_STATE","105"),

        ("TPM_LOC_CTRL","07"),

        ("TPM_LOC_STS","03"),

        ("TPM_CRB_INTF_ID","0000000000006001"),

        ("TPM_CRB_CTRL_REQ","01"),

        ("TPM_CRB_CTRL_STS","02"),

        ("TPM_CRB_CTRL_CANCEL","01"),

        ("TPM_CRB_CTRL_START","01"),

        ("TPM_CRB_INT_ENABLE","80000003"),

        ("TPM_CRB_INT_STS","03"),

        ("TPM_CRB_CTRL_CMD_SIZE","1000"),

        ("TPM_CRB_CTRL_CMD_LADDR","FED40080"),

        ("TPM_CRB_CTRL_CMD_HADDR","00"),

        ("TPM_CRB_CTRL_RSP_SIZE","1000"),

        ("TPM_CRB_CTRL_RSP_ADDR","FED40080"),

        ("TPM_CRB_DATA_BUFFER",["80","01"])


    ]



    for reg,payload in tests:


        print("\n==============================")
        print(reg)
        print("==============================")


        result = decode_register_payload(

            reg,

            payload,

            "READ"

        )


        print("\nDESCRIPTION:")

        print(result["description"])


        print("\nSUMMARY:")

        print(result["summary"])



    print("\nALL REGISTER TESTS COMPLETE\n")