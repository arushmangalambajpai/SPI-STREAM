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
TPM_ACCESS Register

The TPM_ACCESS register manages TPM locality ownership and arbitration. It allows software to request, release and monitor locality ownership while providing information regarding TPM establishment and locality status.

------------------------------------------------------------

[7] tpmRegValidSts = {valid}

Purpose:
Indicates whether all other bits in this register contain valid values.

Current Interpretation:
{"The TPM confirms that all status bits in this register are valid and may be trusted." if valid else "The TPM indicates that the register contents are not currently valid. Other fields should be interpreted with caution."}


[6] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[5] activeLocality = {active}

Purpose:
Indicates whether the current locality owns the TPM.
Writing this bit relinquishes locality ownership.

Current Interpretation:
{"The current locality is active and presently owns the TPM." if active else "The current locality does not currently own the TPM."}


[4] beenSeized = {seized}

Purpose:
Indicates whether control of the TPM has been seized by a higher-priority locality.
Writing this bit clears the flag.

Current Interpretation:
{"A higher-priority locality has taken ownership of the TPM." if seized else "No locality seizure has been reported."}


[3] Seize

Purpose:
Write-only bit used to force TPM ownership to the requesting higher-priority locality.

Current Interpretation:
Read operations always return 0.


[2] pendingRequest = {pending}

Purpose:
Indicates whether another locality is requesting ownership of the TPM.

Current Interpretation:
{"Another locality is currently requesting TPM ownership." if pending else "No pending ownership requests from other localities are reported."}


[1] requestUse = {request}

Purpose:
Indicates whether this locality is requesting ownership of the TPM.
Writing this bit requests active locality ownership.

Current Interpretation:
{"This locality is requesting ownership of the TPM and is waiting for arbitration." if request else "This locality is not requesting TPM ownership."}


[0] tpmEstablishment = {establish}

Purpose:
Indicates whether a Dynamic OS has previously been established on this platform.

Current Interpretation:
{"A Dynamic OS has not previously been established on this platform." if establish else "A Dynamic OS has previously been established on this platform."}

"""


        #
        # Register Summary
        #

        if not valid:

            summary = """
The TPM_ACCESS register reports that its contents are currently invalid. The present register values do not provide sufficient information to reliably determine the locality ownership state.
"""

        elif seized:

            summary = """
The TPM reports that ownership of the TPM has been seized by a higher-priority locality. The current locality no longer controls the TPM until ownership is relinquished.
"""

        elif active and pending:

            summary = """
The current locality owns the TPM, while another locality is simultaneously requesting ownership. TPM locality arbitration is currently in progress.
"""

        elif active:

            summary = """
The current locality successfully owns the TPM and is permitted to communicate with the device. No higher-priority ownership change is currently indicated.
"""

        elif request:

            summary = """
The current locality has requested ownership of the TPM but has not yet become the active locality. The request is awaiting TPM locality arbitration.
"""

        elif pending:

            summary = """
The TPM reports that another locality is requesting ownership. The current register values do not indicate that this locality presently controls the TPM.
"""

        else:

            summary = """
The TPM_ACCESS register does not indicate an active locality request or ownership transition. The current register values do not provide sufficient information to infer additional TPM locality activity.
"""


    else:


        relinquish = get_bit(value,5)
        seize = get_bit(value,3)
        request = get_bit(value,1)


        description += f"""
TPM_ACCESS Register

The TPM_ACCESS register allows software to request, release or seize TPM locality ownership. During write operations, only defined control bits influence TPM locality arbitration.

------------------------------------------------------------

[5] activeLocality = {relinquish}

Purpose:
Writing a value of 1 relinquishes ownership of the current locality.

Current Interpretation:
{"The host requested that the current locality release TPM ownership." if relinquish else "No locality release was requested."}


[3] Seize = {seize}

Purpose:
Requests forced TPM ownership for a higher-priority locality.

Current Interpretation:
{"The host requested a locality seizure operation." if seize else "No locality seizure was requested."}


[1] requestUse = {request}

Purpose:
Requests ownership of the TPM for the current locality.

Current Interpretation:
{"The host requested TPM ownership for the current locality." if request else "No locality ownership request was issued."}

"""


        #
        # Register Summary
        #

        if seize:

            summary = """
The host initiated a TPM locality seizure request, asking the TPM to transfer ownership to a higher-priority locality if permitted.
"""

        elif relinquish:

            summary = """
The host relinquished ownership of the current TPM locality, allowing another locality to acquire control.
"""

        elif request:

            summary = """
The host requested ownership of the TPM for the current locality. The result of this request will be reflected in subsequent TPM_ACCESS register reads.
"""

        else:

            summary = """
No TPM locality control operation was requested by this write. The current register values do not provide sufficient information to determine a specific locality management action.
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

    command = get_bit(value,7)

    locality = get_bit(value,2)

    sts = get_bit(value,1)

    data = get_bit(value,0)


    description += f"""
TPM_INT_ENABLE Register

The TPM_INT_ENABLE register configures the TPM interrupt generation mechanism. It enables or disables individual interrupt sources while providing a global interrupt enable that controls whether enabled interrupt sources are allowed to generate TPM interrupts.

------------------------------------------------------------

[31] globalIntEnable = {global_enable}

Purpose:
Controls the global TPM interrupt enable.
When set, interrupts enabled by the individual interrupt enable bits may be generated.
When cleared, all TPM interrupts are disabled regardless of the remaining enable bits.

Current Interpretation:
{"Global TPM interrupt generation is enabled." if global_enable else "Global TPM interrupt generation is disabled."}


[30:8] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[7] commandReadyIntEnable = {command}

Purpose:
Enables interrupt generation whenever the TPM enters the Command Ready state.

Current Interpretation:
{"Command Ready interrupt generation is enabled." if command else "Command Ready interrupt generation is disabled."}


[6:5] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[4:3] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[2] localityChangeIntEnable = {locality}

Purpose:
Enables interrupt generation whenever TPM locality ownership changes.

Current Interpretation:
{"Locality Change interrupt generation is enabled." if locality else "Locality Change interrupt generation is disabled."}


[1] stsValidIntEnable = {sts}

Purpose:
Enables interrupt generation whenever the TPM Status Register becomes valid.

Current Interpretation:
{"Status Valid interrupt generation is enabled." if sts else "Status Valid interrupt generation is disabled."}


[0] dataAvailIntEnable = {data}

Purpose:
Enables interrupt generation whenever response data becomes available.

Current Interpretation:
{"Data Available interrupt generation is enabled." if data else "Data Available interrupt generation is disabled."}

"""


    #
    # Register Summary
    #

    if not global_enable:

        summary = """
The TPM interrupt system is globally disabled. Although individual interrupt sources may be configured, none are permitted to generate interrupts while the Global Interrupt Enable bit remains cleared.
"""

    else:

        enabled = []

        if command:
            enabled.append("Command Ready")

        if locality:
            enabled.append("Locality Change")

        if sts:
            enabled.append("Status Valid")

        if data:
            enabled.append("Data Available")


        if len(enabled) == 0:

            summary = """
Global TPM interrupt generation is enabled; however, no individual interrupt sources are currently enabled. The current register values do not indicate that any TPM interrupt events will be generated.
"""

        elif len(enabled) == 1:

            summary = f"""
Global TPM interrupt generation is enabled. The TPM is configured to generate interrupts for the {enabled[0]} event.
"""

        else:

            summary = f"""
Global TPM interrupt generation is enabled. The TPM is configured to generate interrupts for the following events: {', '.join(enabled[:-1])} and {enabled[-1]}.
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


    description = f"""
TPM_INT_VECTOR Register

The TPM_INT_VECTOR register specifies the interrupt vector assigned to the TPM. This vector is used by the platform interrupt controller and operating system to identify TPM-generated interrupt requests.

------------------------------------------------------------

[7:0] SIRQVector = {value} (0x{value:02X})

Purpose:
Specifies the interrupt vector associated with TPM interrupt requests.

Current Interpretation:
The TPM interrupt vector is currently configured to {value} (0x{value:02X}). The TPM specification does not define the functional meaning of individual vector values, as they are platform and operating system dependent.
"""


    summary = f"""
The TPM interrupt vector is configured to {value} (0x{value:02X}). The current register value identifies the interrupt vector assigned to TPM interrupt requests; however, additional platform-specific information is required to determine how this vector is mapped by the interrupt controller.
"""


    return make_output(
        description,
        summary
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


    if operation == "READ":


        description += f"""
TPM_INT_STATUS Register

The TPM_INT_STATUS register reports which TPM interrupt events have occurred. Individual interrupt status bits are asserted when their corresponding TPM events occur and remain set until cleared by software.

------------------------------------------------------------

[31:8] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[7] commandReadyIntOccurred = {cmd}

Purpose:
Indicates that the TPM_STS.commandReady field transitioned from 0 to 1.

Current Interpretation:
{"A Command Ready interrupt event has occurred." if cmd else "No Command Ready interrupt event is currently reported."}


[6:3] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[2] localityChangeIntOccurred = {loc}

Purpose:
Indicates that a TPM locality change interrupt has occurred.

Current Interpretation:
{"A locality change interrupt has been reported." if loc else "No locality change interrupt is currently reported."}


[1] stsValidIntOccurred = {sts}

Purpose:
Indicates that the TPM_STS.stsValid field transitioned from 0 to 1.

Current Interpretation:
{"A Status Valid interrupt event has occurred." if sts else "No Status Valid interrupt event is currently reported."}


[0] dataAvailIntOccurred = {data}

Purpose:
Indicates that TPM response data became available for reading.

Current Interpretation:
{"A Data Available interrupt event has occurred." if data else "No Data Available interrupt event is currently reported."}

"""


        #
        # Register Summary
        #

        events = []

        if cmd:
            events.append("Command Ready")

        if loc:
            events.append("Locality Change")

        if sts:
            events.append("Status Valid")

        if data:
            events.append("Data Available")


        if len(events) == 0:

            summary = """
The TPM is not currently reporting any pending interrupt events. The current register values do not indicate that any interrupt conditions have occurred.
"""

        elif len(events) == 1:

            summary = f"""
The TPM reports a pending {events[0]} interrupt event.
"""

        else:

            summary = f"""
The TPM reports multiple pending interrupt events, including {', '.join(events[:-1])} and {events[-1]}. These interrupt status flags remain asserted until cleared by software.
"""


    else:


        description += f"""
TPM_INT_STATUS Register

The TPM_INT_STATUS register allows software to acknowledge and clear previously reported TPM interrupt events. Writing a value of 1 to a defined interrupt status bit clears that interrupt, while writing 0 has no effect.

------------------------------------------------------------

[7] commandReadyIntOccurred = {cmd}

Purpose:
Writing a value of 1 clears the Command Ready interrupt.

Current Interpretation:
{"The host requested that the Command Ready interrupt be cleared." if cmd else "The Command Ready interrupt was not selected for clearing."}


[2] localityChangeIntOccurred = {loc}

Purpose:
Writing a value of 1 clears the Locality Change interrupt.

Current Interpretation:
{"The host requested that the Locality Change interrupt be cleared." if loc else "The Locality Change interrupt was not selected for clearing."}


[1] stsValidIntOccurred = {sts}

Purpose:
Writing a value of 1 clears the Status Valid interrupt.

Current Interpretation:
{"The host requested that the Status Valid interrupt be cleared." if sts else "The Status Valid interrupt was not selected for clearing."}


[0] dataAvailIntOccurred = {data}

Purpose:
Writing a value of 1 clears the Data Available interrupt.

Current Interpretation:
{"The host requested that the Data Available interrupt be cleared." if data else "The Data Available interrupt was not selected for clearing."}

"""


        cleared = []

        if cmd:
            cleared.append("Command Ready")

        if loc:
            cleared.append("Locality Change")

        if sts:
            cleared.append("Status Valid")

        if data:
            cleared.append("Data Available")


        if len(cleared) == 0:

            summary = """
No TPM interrupt status flags were selected for clearing. The current register values do not indicate that any interrupt acknowledgement operation was requested.
"""

        elif len(cleared) == 1:

            summary = f"""
The host acknowledged and cleared the pending {cleared[0]} interrupt event.
"""

        else:

            summary = f"""
The host acknowledged and cleared multiple TPM interrupt events, including {', '.join(cleared[:-1])} and {cleared[-1]}.
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

    cmd_ready = get_bit(value,7)
    edge_falling = get_bit(value,6)
    edge_rising = get_bit(value,5)
    level_low = get_bit(value,4)
    level_high = get_bit(value,3)
    locality = get_bit(value,2)
    sts = get_bit(value,1)
    data = get_bit(value,0)


    #
    # Decode helper strings
    #

    interface_version = {
        0: "Reserved",
        1: "FIFO Interface (defined by the TPM PTP specification)"
    }.get(version, "Reserved / Vendor Defined")


    transfer_support = {
        0: "Legacy transfer size only (supports legacy transfers).",
        1: "Maximum transfer size of 8 bytes (includes legacy transfers).",
        2: "Maximum transfer size of 32 bytes (includes 8-byte and legacy transfers).",
        3: "Maximum transfer size of 64 bytes (includes 32-byte, 8-byte and legacy transfers)."
    }


    description += f"""
TPM_INTF_CAPABILITY Register

The TPM_INTF_CAPABILITY register describes the communication capabilities implemented by the TPM. It reports the supported FIFO interface version, maximum transfer size, burst count behaviour and available interrupt generation mechanisms.

------------------------------------------------------------

[31] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[30:28] InterfaceVersion = {version}

Purpose:
Identifies the FIFO interface version implemented by the TPM.

Current Interpretation:
{interface_version}


[27:11] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[10:9] DataTransferSizeSupport = {transfer}

Purpose:
Indicates the maximum transaction size supported by the TPM FIFO interface.

Current Interpretation:
{transfer_support.get(transfer, "The reported transfer capability is not defined by the TPM specification.")}


[8] BurstCountStatic = {burst_static}

Purpose:
Indicates whether the TPM_STS.burstCount value is fixed or dynamic.

Current Interpretation:
{"The reported burst count remains constant." if burst_static else "The reported burst count may change dynamically during communication."}


[7] CommandReadyIntSupport = {cmd_ready}

Purpose:
Indicates support for Command Ready interrupts.

Current Interpretation:
{"Command Ready interrupt generation is supported." if cmd_ready else "Command Ready interrupt generation is not supported."}


[6] InterruptEdgeFalling = {edge_falling}

Purpose:
Indicates support for falling-edge triggered interrupts.

Current Interpretation:
{"Falling-edge interrupt triggering is supported." if edge_falling else "Falling-edge interrupt triggering is not supported."}


[5] InterruptEdgeRising = {edge_rising}

Purpose:
Indicates support for rising-edge triggered interrupts.

Current Interpretation:
{"Rising-edge interrupt triggering is supported." if edge_rising else "Rising-edge interrupt triggering is not supported."}


[4] InterruptLevelLow = {level_low}

Purpose:
Indicates support for active-low level interrupts.

Current Interpretation:
{"Active-low level interrupts are supported." if level_low else "Active-low level interrupts are not supported."}


[3] InterruptLevelHigh = {level_high}

Purpose:
Indicates support for active-high level interrupts.

Current Interpretation:
{"Active-high level interrupts are supported." if level_high else "Active-high level interrupts are not supported."}


[2] LocalityChangeIntSupport = {locality}

Purpose:
Indicates support for Locality Change interrupts.

Current Interpretation:
{"Locality Change interrupt generation is supported." if locality else "Locality Change interrupt generation is not supported."}


[1] StsValidIntSupport = {sts}

Purpose:
Indicates support for Status Valid interrupts.

Current Interpretation:
{"Status Valid interrupt generation is supported." if sts else "Status Valid interrupt generation is not supported."}


[0] DataAvailIntSupport = {data}

Purpose:
Indicates support for Data Available interrupts.

Current Interpretation:
{"Data Available interrupt generation is supported." if data else "Data Available interrupt generation is not supported."}

"""


    #
    # Register Summary
    #

    summary = f"""
The TPM reports support for the {interface_version.lower()} with a maximum FIFO transfer size of {transfer_support[transfer].lower()} Burst Count values are {"static" if burst_static else "dynamic"}.
"""

    interrupts = []

    if cmd_ready:
        interrupts.append("Command Ready")

    if locality:
        interrupts.append("Locality Change")

    if sts:
        interrupts.append("Status Valid")

    if data:
        interrupts.append("Data Available")


    trigger_modes = []

    if edge_rising:
        trigger_modes.append("rising-edge")

    if edge_falling:
        trigger_modes.append("falling-edge")

    if level_high:
        trigger_modes.append("active-high level")

    if level_low:
        trigger_modes.append("active-low level")


    if interrupts:

        if len(interrupts) == 1:

            summary += f"""
The TPM supports the {interrupts[0]} interrupt.
"""

        else:

            summary += f"""
The TPM supports the following interrupt sources: {', '.join(interrupts[:-1])} and {interrupts[-1]}.
"""

    else:

        summary += """
The current register values do not indicate support for any optional TPM interrupt sources.
"""


    if trigger_modes:

        if len(trigger_modes) == 1:

            summary += f"""
Supported interrupt signalling mode: {trigger_modes[0]}.
"""

        else:

            summary += f"""
Supported interrupt signalling modes include {', '.join(trigger_modes[:-1])} and {trigger_modes[-1]}.
"""

    else:

        summary += """
The current register values do not provide sufficient information to determine any supported interrupt signalling modes.
"""


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

        retry = get_bit(value,1)


        family_text = {

            0 : "TPM 1.2 Family",

            1 : "TPM 2.0 Family",

            2 : "Reserved",

            3 : "Reserved"

        }


        description += f"""
TPM_STS Register

The TPM_STS register is the primary status and control register of the TPM FIFO interface. It reports the current execution state of the TPM while also controlling command execution, cancellation and FIFO communication. During TPM transactions, this register is repeatedly accessed by the host to determine when commands may be transmitted and when responses are available.

------------------------------------------------------------

[31:28] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[27:26] tpmFamily = {family}

Purpose:
Identifies the TPM family implemented by the device.

Current Interpretation:
{family_text.get(family, "Unknown TPM family.")}


[25] resetEstablishmentBit

Purpose:
Write-only control bit used to reset the TPM establishment flag.

Current Interpretation:
Not applicable during read operations.


[24] commandCancel

Purpose:
Write-only control bit used to cancel the currently executing TPM command.

Current Interpretation:
Not applicable during read operations.


[23:8] burstCount = {burst}

Purpose:
Indicates the maximum number of bytes that may be transferred through the FIFO before the TPM should be polled again.

Current Interpretation:
The TPM currently permits a burst transfer of {burst} byte(s).


[7] stsValid = {valid}

Purpose:
Indicates whether the TPM_STS register contents are valid.

Current Interpretation:
{"The TPM reports that the status register contents are valid." if valid else "The TPM reports that the status register contents are not currently valid."}


[6] commandReady = {ready}

Purpose:
Indicates that the TPM is ready to receive a new command.

Current Interpretation:
{"The TPM is currently ready to accept a new command." if ready else "The TPM is not currently advertising the Command Ready state."}


[5] tpmGo

Purpose:
Write-only control bit used to instruct the TPM to begin command execution.

Current Interpretation:
Not applicable during read operations.


[4] dataAvail = {data}

Purpose:
Indicates whether TPM response data is available within the FIFO.

Current Interpretation:
{"Response data is currently available for reading." if data else "No response data is currently available."}


[3] expect = {expect}

Purpose:
Indicates whether the TPM expects additional command bytes.

Current Interpretation:
{"The TPM expects additional command bytes before execution can begin." if expect else "The TPM is not requesting additional command data."}


[2] selfTestDone = {selftest}

Purpose:
Indicates whether TPM self-test has completed.

Current Interpretation:
{"The TPM reports that self-test has completed." if selftest else "The TPM self-test has not yet completed or completion is not currently indicated."}


[1] responseRetry = {retry}

Purpose:
Indicates whether the host should request retransmission of the previous response.

Current Interpretation:
{"The TPM indicates that the previous response may be retransmitted if requested." if retry else "No response retransmission condition is currently indicated."}


[0] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.

"""


        #
        # Register Summary
        #

        if not valid:

            summary = """
The TPM_STS register contents are currently reported as invalid. The remaining status fields do not provide sufficient information to reliably determine the current TPM execution state.
"""

        elif data:

            summary = f"""
The TPM has completed command execution and response data is available for retrieval from the FIFO. The current burst count permits up to {burst} byte(s) to be transferred before another status check is required.
"""

        elif expect:

            summary = f"""
The TPM is actively receiving a command and expects additional command bytes before execution can begin. The current burst count permits up to {burst} byte(s) to be transferred during the present FIFO transaction.
"""

        elif ready:

            summary = f"""
The TPM is ready to receive a new command from the host. The reported burst count is {burst} byte(s), indicating the maximum FIFO transfer currently supported before another status poll.
"""

        elif selftest:

            summary = f"""
The TPM reports that its internal self-test has completed successfully. The current burst count is {burst} byte(s).
"""

        elif retry:

            summary = """
The TPM indicates that the previous response may be retransmitted if the host issues a Response Retry request.
"""

        else:

            summary = f"""
The TPM reports a valid status register; however, the current register values do not indicate a specific command processing state. The reported burst count is {burst} byte(s).
"""



    else:
        
        reset = get_bit(value,25)

        cancel = get_bit(value,24)

        ready = get_bit(value,6)

        go = get_bit(value,5)

        retry = get_bit(value,1)


        description += f"""
TPM_STS Register

The TPM_STS register also provides the primary control interface for FIFO-based TPM communication. During write operations, software uses this register to reset TPM command state, cancel command execution, initiate command processing and request response retransmission.

------------------------------------------------------------

[31:28] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[27:26] tpmFamily

Purpose:
Read-only field identifying the TPM family.

Current Interpretation:
Not applicable during write operations.


[25] resetEstablishmentBit = {reset}

Purpose:
Writing a value of 1 resets the TPM Establishment Flag if the platform permits this operation.

Current Interpretation:
{"The host requested that the TPM Establishment Flag be reset." if reset else "No TPM Establishment Flag reset was requested."}


[24] commandCancel = {cancel}

Purpose:
Writing a value of 1 requests cancellation of the currently executing TPM command.

Current Interpretation:
{"The host requested cancellation of the currently executing TPM command." if cancel else "No TPM command cancellation was requested."}


[23:8] burstCount

Purpose:
Read-only field indicating FIFO transfer capacity.

Current Interpretation:
Not applicable during write operations.


[7] stsValid

Purpose:
Read-only status bit.

Current Interpretation:
Not applicable during write operations.


[6] commandReady = {ready}

Purpose:
Writing a value of 1 resets the TPM command state and prepares the TPM to receive a new command.

Current Interpretation:
{"The host requested that the TPM enter the Command Ready state." if ready else "No Command Ready request was issued."}


[5] tpmGo = {go}

Purpose:
Writing a value of 1 instructs the TPM to begin execution of the previously transmitted command.

Current Interpretation:
{"The host requested execution of the queued TPM command." if go else "No TPM command execution request was issued."}


[4] dataAvail

Purpose:
Read-only status bit.

Current Interpretation:
Not applicable during write operations.


[3] expect

Purpose:
Read-only status bit.

Current Interpretation:
Not applicable during write operations.


[2] selfTestDone

Purpose:
Read-only status bit.

Current Interpretation:
Not applicable during write operations.


[1] responseRetry = {retry}

Purpose:
Writing a value of 1 requests retransmission of the previous TPM response.

Current Interpretation:
{"The host requested retransmission of the previous TPM response." if retry else "No TPM response retransmission request was issued."}


[0] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.

"""


        #
        # Register Summary
        #

        actions = []

        if reset:
            actions.append("reset the TPM Establishment Flag")

        if cancel:
            actions.append("cancel the currently executing TPM command")

        if ready:
            actions.append("place the TPM into the Command Ready state")

        if go:
            actions.append("begin execution of the queued TPM command")

        if retry:
            actions.append("request retransmission of the previous TPM response")


        if len(actions) == 0:

            summary = """
No TPM control operation was requested through the TPM_STS register. The current register values do not indicate a specific TPM command control action.
"""

        elif len(actions) == 1:

            summary = f"""
The host requested the TPM to {actions[0]}.
"""

        else:

            summary = f"""
The host issued multiple TPM control operations through the TPM_STS register, requesting the TPM to {', '.join(actions[:-1])} and {actions[-1]}.
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

    lock = get_bit(value,19)

    selector = get_bits(value,18,17)

    crb = get_bit(value,14)

    fifo = get_bit(value,13)

    locality = get_bit(value,8)

    version = get_bits(value,7,4)

    interface = get_bits(value,3,0)


    checksum_text = {

        0: "The TPM does not support command/response checksum calculation.",

        1: "The TPM supports explicit checksum calculation for commands and responses.",

        2: "The TPM supports implicit checksum calculation for commands and responses."

    }


    selector_text = {

        0: "TIS (FIFO) interface is selected.",

        1: "CRB interface is selected."

    }


    interface_type = {

        0: "FIFO interface is active.",

        1: "CRB interface is active.",

        15: "Reserved for legacy compatibility."

    }


    description += f"""
TPM_INTERFACE_ID Register

The TPM_INTERFACE_ID register identifies the communication interfaces and capabilities implemented by the TPM. It reports the currently selected interface, supported interface types, checksum capabilities, locality support and interface revision information.

------------------------------------------------------------

[31:24] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[23:22] CapSPICSUM = {checksum}

Purpose:
Indicates whether the TPM supports checksum calculation for commands and responses.

Current Interpretation:
{checksum_text.get(checksum, "The reported checksum capability is reserved or undefined by the TPM specification.")}


[21:20] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[19] IntfSelLock = {lock}

Purpose:
Indicates whether the InterfaceSelector field has been locked against further modification.

Current Interpretation:
{"The interface selection has been locked and can no longer be modified until the next TPM initialization." if lock else "The interface selection remains configurable."}


[18:17] InterfaceSelector = {selector}

Purpose:
Indicates the interface currently selected by the TPM.

Current Interpretation:
{selector_text.get(selector, "The selected interface value is reserved by the TPM specification.")}


[16:15] CapIFRes = 0

Purpose:
Reserved for future interface definitions.

Current Interpretation:
No interpretation is defined.


[14] CapCRB = {crb}

Purpose:
Indicates whether the CRB interface is supported.

Current Interpretation:
{"The TPM supports the CRB interface." if crb else "The TPM does not support the CRB interface."}


[13] CapFIFO = {fifo}

Purpose:
Indicates whether the FIFO (TIS) interface is supported.

Current Interpretation:
{"The TPM supports the FIFO interface." if fifo else "The TPM does not support the FIFO interface."}


[12:9] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[8] CapLocality = {locality}

Purpose:
Indicates the number of supported TPM localities.

Current Interpretation:
{"The TPM supports Localities 0 through 4." if locality else "The TPM supports only Locality 0."}


[7:4] InterfaceVersion = {version}

Purpose:
Identifies the implemented interface revision.

Current Interpretation:
{"Interface Version 0 (FIFO interface for TPM 2.0)." if version == 0 else f"Interface Version {version}."}


[3:0] InterfaceType = {interface}

Purpose:
Identifies the interface currently active.

Current Interpretation:
{interface_type.get(interface, "The reported interface type is reserved or vendor-defined.")}

"""


    #
    # Register Summary
    #

    supported = []

    if fifo:
        supported.append("FIFO")

    if crb:
        supported.append("CRB")


    summary = ""

    if len(supported) == 2:

        summary += """
The TPM supports both FIFO and CRB communication interfaces.
"""

    elif len(supported) == 1:

        summary += f"""
The TPM supports the {supported[0]} communication interface.
"""

    else:

        summary += """
The current register values do not indicate support for either the FIFO or CRB communication interface.
"""


    summary += f"""
The active interface is reported as {interface_type.get(interface, 'an implementation-defined interface').lower()}
"""

    summary += f"""
The interface selector currently indicates {selector_text.get(selector, 'a reserved interface selection').lower()}
"""

    if lock:

        summary += """
The interface selection has been locked and cannot be modified until the next TPM initialization.
"""

    else:

        summary += """
The interface selection remains configurable.
"""


    if locality:

        summary += """
The TPM supports all five TPM localities (0-4).
"""

    else:

        summary += """
The TPM supports only Locality 0.
"""


    summary += f"""
The reported interface revision is {version}.
"""


    if checksum == 0:

        summary += """
The TPM does not support command or response checksum calculation.
"""

    elif checksum == 1:

        summary += """
The TPM supports explicit command and response checksum calculation.
"""

    elif checksum == 2:

        summary += """
The TPM supports implicit command and response checksum calculation.
"""

    else:

        summary += """
The current register values do not provide sufficient information to determine the TPM checksum capability.
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


    value = payload_to_int(payload)

    description = ""

    summary = ""


    request = get_bit(value,1)

    enable = get_bit(value,0)


    description += f"""
TPM_DATA_CSUM_ENABLE Register

The TPM_DATA_CSUM_ENABLE register controls the TPM data checksum mechanism. It enables implicit checksum calculation for TPM command and response transfers and allows software to explicitly request checksum calculation during command reception.

------------------------------------------------------------

[31:2] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[1] dataCSumRequest = {request}

Purpose:
Requests explicit data checksum calculation while the TPM is receiving a command.

Current Interpretation:
{"The host has explicitly requested TPM data checksum calculation." if request else "No explicit data checksum request is currently indicated."}


[0] dataCSumEnable = {enable}

Purpose:
Enables implicit TPM data checksum calculation for command and response transfers.

Current Interpretation:
{"Implicit TPM data checksum calculation is enabled." if enable else "Implicit TPM data checksum calculation is disabled."}

"""


    #
    # Register Summary
    #

    if enable and request:

        summary = """
Implicit TPM data checksum calculation is enabled, and an explicit checksum calculation has been requested for the current command reception.
"""

    elif enable:

        summary = """
Implicit TPM data checksum calculation is enabled for TPM command and response transfers.
"""

    elif request:

        summary = """
An explicit TPM data checksum calculation has been requested, while implicit checksum calculation remains disabled.
"""

    else:

        summary = """
TPM data checksum calculation is disabled, and no explicit checksum calculation request is currently indicated.
"""


    return make_output(
        description,
        summary
    )
# ==========================================================
# FIFO : DATA CHECKSUM
# ==========================================================

def decode_TPM_DATA_CSUM(
        payload,
        operation
    ):


    value = payload_to_int(payload)

    checksum = value & 0xFFFF


    description = f"""
TPM_DATA_CSUM Register

The TPM_DATA_CSUM register stores the 16-bit checksum generated by the TPM whenever data checksum functionality is enabled. During command reception it contains the checksum of the complete TPM command, while during response transmission it contains the checksum of the complete TPM response.

------------------------------------------------------------

[31:16] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[15:0] dataChecksum = 0x{checksum:04X} ({checksum})

Purpose:
Contains the 16-bit checksum calculated over the complete TPM command or TPM response. A checksum is a mathematical value computed from the transmitted data and is used as an integrity check. By comparing this checksum with one calculated independently from the received data, software can detect accidental data corruption during communication.

Current Interpretation:
The TPM currently reports a checksum value of 0x{checksum:04X} ({checksum}). This value represents the calculated integrity checksum for the associated TPM command or response.
"""


    if checksum == 0:

        summary = """
The TPM reports a checksum value of 0x0000 (0). This may indicate that checksum functionality is disabled, no checksum has been generated, or that the calculated checksum is zero. The current register value alone is insufficient to determine which condition applies.
"""

    else:

        summary = f"""
The TPM reports a 16-bit data checksum value of 0x{checksum:04X} ({checksum}) for the associated TPM command or response. This checksum may be compared with an independently calculated checksum to verify the integrity of the transmitted data.
"""


    return make_output(
        description,
        summary
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


    vendor_name = {

        0x4946: "Infineon Technologies",

        0x4154: "Atmel / Microchip",

        0x4E54: "Nuvoton Technology",

        0x534D: "STMicroelectronics",

        0x5745: "Winbond",

        0x4942: "IBM"

    }.get(
        vid,
        "Unknown / Vendor-specific"
    )


    description = f"""
TPM_DID_VID Register

The TPM_DID_VID register identifies the TPM manufacturer and the TPM device model. It allows software to determine the vendor responsible for the TPM implementation and the corresponding vendor-specific device identifier.

------------------------------------------------------------

[31:16] DID (Device ID) = 0x{did:04X} ({did})

Purpose:
Contains the vendor-defined TPM Device Identifier. The interpretation of this value is specific to the TPM manufacturer and uniquely identifies a TPM device or product family.

Current Interpretation:
The TPM reports a Device ID of 0x{did:04X} ({did}).


[15:0] VID (Vendor ID) = 0x{vid:04X} ({vid})

Purpose:
Contains the TPM Vendor Identifier assigned by the Trusted Computing Group (TCG). This value identifies the manufacturer of the TPM.

Current Interpretation:
The TPM reports Vendor ID 0x{vid:04X} ({vid}), corresponding to {vendor_name}.
"""


    summary = f"""
The TPM identifies itself as a device manufactured by {vendor_name}. The reported Vendor ID is 0x{vid:04X} ({vid}) and the vendor-specific Device ID is 0x{did:04X} ({did}).
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# FIFO : REVISION ID
# ==========================================================

def decode_TPM_RID(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = f"""
TPM_RID Register

The TPM_RID register identifies the hardware revision of the TPM implementation. The Revision ID (RID) is assigned by the TPM manufacturer and is used to distinguish different hardware revisions or versions of the same TPM device.

------------------------------------------------------------

[7:0] RID (Revision ID) = 0x{value:02X} ({value})

Purpose:
Specifies the hardware Revision ID of the TPM component. This value is vendor-specific and identifies the particular revision of the TPM implementation.

Current Interpretation:
The TPM reports a Revision ID of 0x{value:02X} ({value}). The interpretation of this revision value is defined by the TPM manufacturer and may be used to distinguish different hardware revisions or device versions.
"""


    summary = f"""
The TPM reports a hardware Revision ID of 0x{value:02X} ({value}). This vendor-defined value identifies the revision of the TPM implementation and may be used to distinguish different hardware versions of the same TPM device.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# FIFO : DATA FIFO
# ==========================================================

def decode_TPM_DATA_FIFO(
        payload,
        operation
    ):


    size = len(payload)


    description = f"""
TPM_DATA_FIFO Register

The TPM_DATA_FIFO register is the primary data transfer register of the TPM FIFO interface. It is used to exchange TPM command and response bytes between the host and the TPM. Data is transferred sequentially through this register until the complete command or response has been transmitted.

Current Transfer Size:
{size} byte(s)

Current Interpretation:
The transferred bytes represent a portion of the TPM communication stream. Depending on the transfer direction, the data may contain a TPM command, TPM response, command parameters or response parameters. Additional TPM command decoding is required to determine the contents of the transferred data.
"""


    if operation == "WRITE":


        summary = f"""
The host transferred {size} byte(s) to the TPM through the FIFO interface. These bytes may contain a TPM command or a portion of a TPM command stream. Further TPM command decoding should be applied to determine the transmitted command and its parameters.
"""


    else:


        summary = f"""
The host received {size} byte(s) from the TPM through the FIFO interface. These bytes may contain a TPM response or a portion of a TPM response stream. Further TPM response decoding should be applied to determine the returned response and its associated parameters.
"""


    return make_output(
        description,
        summary
    )


# ==========================================================
# FIFO : EXTENDED DATA FIFO
# ==========================================================


def decode_TPM_XDATA_FIFO(
        payload,
        operation
    ):


    size = len(payload)


    description = f"""
TPM_XDATA_FIFO Register

The TPM_XDATA_FIFO register provides an extended FIFO data transfer mechanism for TPM communication. Like the standard TPM_DATA_FIFO register, it is used to exchange TPM command and response bytes between the host and the TPM. Data transferred through this register forms part of the TPM communication stream and requires higher-level protocol decoding for interpretation.

Current Transfer Size:
{size} byte(s)

Current Interpretation:
The transferred bytes represent a portion of an extended TPM communication stream. Depending on the transfer direction, the data may contain TPM commands, TPM responses or associated parameters. Additional TPM command or response decoding is required to determine the contents of the transferred data.
"""


    if operation == "WRITE":


        summary = f"""
The host transferred {size} byte(s) to the TPM through the Extended FIFO interface. These bytes may contain a TPM command or a portion of a TPM command stream. Further TPM command decoding should be applied to determine the transmitted command and its parameters.
"""


    else:


        summary = f"""
The host received {size} byte(s) from the TPM through the Extended FIFO interface. These bytes may contain a TPM response or a portion of a TPM response stream. Further TPM response decoding should be applied to determine the returned response and its associated parameters.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : TPM_LOC_STATE
# ==========================================================

def decode_TPM_LOC_STATE(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    valid = get_bit(value,7)

    locality = get_bits(value,4,2)

    assigned = get_bit(value,1)

    established = get_bit(value,0)


    locality_text = {

        0: "Locality 0",

        1: "Locality 1",

        2: "Locality 2",

        3: "Locality 3",

        4: "Locality 4"

    }


    description = f"""
TPM_LOC_STATE Register

The TPM_LOC_STATE register reports the current TPM locality state for the CRB interface. It indicates whether the register contents are valid, which locality currently owns the TPM, whether a locality has been assigned, and the TPM establishment status.

------------------------------------------------------------

[31:8] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[7] tpmRegValidSts = {valid}

Purpose:
Indicates whether all remaining fields of this register contain valid values.

Current Interpretation:
{"The TPM reports that the register contents are valid." if valid else "The TPM reports that the register contents are not currently valid."}


[6:5] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[4:2] activeLocality = {locality}

Purpose:
Identifies the locality that currently has access to the TPM.

Current Interpretation:
{locality_text.get(locality, "Reserved locality value reported by the TPM.")}


[1] locAssigned = {assigned}

Purpose:
Indicates whether a TPM locality has been assigned.

Current Interpretation:
{"A TPM locality is currently assigned." if assigned else "No TPM locality is currently assigned."}


[0] tpmEstablished = {established}

Purpose:
Indicates the TPM Establishment state.

Current Interpretation:
{"The TPM Establishment flag is set." if established else "The TPM Establishment flag is cleared."}

"""


    #
    # Register Summary
    #

    if not valid:

        summary = """
The TPM reports that the TPM_LOC_STATE register contents are currently invalid. The remaining register values do not provide sufficient information to determine the current locality state.
"""

    elif assigned:

        summary = f"""
The TPM reports that {locality_text.get(locality, 'a reserved locality')} currently owns the TPM. A locality has been successfully assigned, and the TPM Establishment flag is {"set" if established else "cleared"}.
"""

    else:

        summary = f"""
No TPM locality is currently assigned. The active locality field reports {locality_text.get(locality, 'a reserved locality')}, and the TPM Establishment flag is {"set" if established else "cleared"}.
"""


    return make_output(
        description,
        summary
    )


# ==========================================================
# CRB : TPM_LOC_CTRL
# ==========================================================


def decode_TPM_LOC_CTRL(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = ""

    summary = ""


    reset = get_bit(value,3)

    bit2 = get_bit(value,2)

    bit1 = get_bit(value,1)

    bit0 = get_bit(value,0)


    description += f"""
TPM_LOC_CTRL Register

The TPM_LOC_CTRL register controls TPM locality ownership in the CRB interface. It allows software to request TPM access, relinquish ownership, seize ownership or initiate locality-controlled TPM operations. The interpretation of Bits [2:0] depends on whether the register belongs to Locality 4 or Localities 0-3.

------------------------------------------------------------

[31:4] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[3] resetEstablishmentBit = {reset}

Purpose:
Resets the TPM_LOC_STATE.tpmEstablished bit when written from Locality 3 or Locality 4.

Current Interpretation:
{"The host requested that the TPM Establishment flag be reset." if reset else "No TPM Establishment reset request was issued."}


[2] = {bit2}

Purpose (Localities 0-3):
Seize
Requests the TPM to transfer ownership to this locality if it has a higher priority.

Purpose (Locality 4):
TPM_HASH_END
Initiates the TPM HASH_END action used during the D-RTM sequence.

Current Interpretation:
{"Bit 2 is asserted. For Localities 0-3 this requests TPM locality seizure. For Locality 4 this initiates the TPM_HASH_END operation. The current register value alone is insufficient to determine which interpretation applies." if bit2 else "Bit 2 is not asserted."}


[1] = {bit1}

Purpose (Localities 0-3):
Relinquish
Indicates that the active locality has completed its TPM operations and relinquishes ownership.

Purpose (Locality 4):
TPM_HASH_DATA
Initiates the TPM HASH_DATA action used during the D-RTM sequence.

Current Interpretation:
{"Bit 1 is asserted. For Localities 0-3 this relinquishes TPM locality ownership. For Locality 4 this initiates the TPM_HASH_DATA operation. The current register value alone is insufficient to determine which interpretation applies." if bit1 else "Bit 1 is not asserted."}


[0] = {bit0}

Purpose (Localities 0-3):
requestAccess
Requests TPM locality ownership and initiates locality arbitration.

Purpose (Locality 4):
TPM_HASH_START
Initiates the TPM HASH_START action used during the D-RTM sequence.

Current Interpretation:
{"Bit 0 is asserted. For Localities 0-3 this requests TPM locality ownership. For Locality 4 this initiates the TPM_HASH_START operation. The current register value alone is insufficient to determine which interpretation applies." if bit0 else "Bit 0 is not asserted."}

"""


    #
    # Register Summary
    #

    actions = []


    if reset:
        actions.append(
            "reset the TPM Establishment flag"
        )

    if bit2:
        actions.append(
            "request TPM locality seizure (Localities 0-3) or initiate TPM_HASH_END (Locality 4)"
        )

    if bit1:
        actions.append(
            "relinquish TPM locality ownership (Localities 0-3) or initiate TPM_HASH_DATA (Locality 4)"
        )

    if bit0:
        actions.append(
            "request TPM locality ownership (Localities 0-3) or initiate TPM_HASH_START (Locality 4)"
        )


    if len(actions) == 0:

        summary = """
No TPM locality control operation was requested. The current register values do not indicate any CRB locality control or D-RTM control actions.
"""

    elif len(actions) == 1:

        summary = f"""
The host requested the TPM to {actions[0]}. The exact interpretation depends on the locality associated with this register access.
"""

    else:

        summary = f"""
The host issued multiple TPM locality control operations, requesting the TPM to {', '.join(actions[:-1])} and {actions[-1]}. The exact interpretation of locality-dependent control bits requires knowledge of the originating locality.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : TPM_LOC_STS
# ==========================================================

def decode_TPM_LOC_STS(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    seized = get_bit(value,1)

    granted = get_bit(value,0)


    description = f"""
TPM_LOC_STS Register

The TPM_LOC_STS register reports the current status of a TPM locality in the CRB interface. It indicates whether the locality has been granted access to the TPM and whether ownership has been seized by a higher-priority locality. This register is maintained independently for each TPM locality.

------------------------------------------------------------

[31:2] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[1] beenSeized = {seized}

Purpose:
Indicates whether control of the TPM has been seized by a higher-priority locality.

Current Interpretation:
{"A higher-priority locality has seized ownership of the TPM from this locality." if seized else "No higher-priority locality has seized TPM ownership from this locality."}


[0] granted = {granted}

Purpose:
Indicates whether this locality has been granted access to the TPM.

Current Interpretation:
{"This locality has been granted access to the TPM." if granted else "This locality has not been granted access to the TPM."}

"""


    #
    # Register Summary
    #

    if granted and seized:

        summary = """
The TPM reports that this locality has been granted access; however, ownership has subsequently been seized by a higher-priority locality.
"""

    elif granted:

        summary = """
The TPM has granted this locality access to the TPM. The locality currently owns the TPM and may perform TPM operations.
"""

    elif seized:

        summary = """
The TPM reports that this locality has lost ownership because a higher-priority locality has seized control of the TPM.
"""

    else:

        summary = """
The TPM has not granted this locality access, and no locality seizure has been reported.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : TPM_CRB_INTF_ID
# ==========================================================

def decode_TPM_CRB_INTF_ID(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    did = get_bits(value,63,48)

    vid = get_bits(value,47,32)

    rid = get_bits(value,31,24)

    checksum = get_bits(value,23,22)

    lock = get_bit(value,19)

    selector = get_bits(value,18,17)

    cap_crb = get_bit(value,14)

    cap_fifo = get_bit(value,13)

    transfer = get_bits(value,12,11)

    chunk = get_bit(value,10)

    idle_bypass = get_bit(value,9)

    locality = get_bit(value,8)

    version = get_bits(value,7,4)

    interface = get_bits(value,3,0)


    vendor_name = {
        0x4946: "Infineon Technologies",
        0x4154: "Atmel / Microchip",
        0x4E54: "Nuvoton Technology",
        0x534D: "STMicroelectronics",
        0x5745: "Winbond",
        0x4942: "IBM"
    }.get(
        vid,
        "Unknown / Vendor-specific"
    )


    checksum_text = {
        0: "The TPM does not support command or response checksum calculation.",
        1: "The TPM supports explicit checksum calculation.",
        2: "The TPM supports implicit checksum calculation."
    }


    transfer_text = {
        0: "Maximum transfer size of 4 bytes.",
        1: "Maximum transfer size of 8 bytes (includes 4-byte transfers).",
        2: "Maximum transfer size of 32 bytes (includes 4-byte and 8-byte transfers).",
        3: "Maximum transfer size of 64 bytes (includes 4-byte, 8-byte and 32-byte transfers)."
    }


    interface_selector = {
        0: "FIFO interface selected.",
        1: "CRB interface selected."
    }


    interface_type = {
        0: "FIFO interface is active.",
        1: "CRB interface is active.",
        2: "ARM CRB interface is active.",
        15: "FIFO interface defined in TIS 1.3 is active."
    }


    description = f"""
TPM_CRB_INTF_ID Register

The TPM_CRB_INTF_ID register identifies the TPM implementation, supported communication interfaces and CRB interface capabilities. It reports manufacturer information, interface selection, supported transfer sizes and additional CRB-specific features.

------------------------------------------------------------

[63:48] DID = 0x{did:04X} ({did})

Purpose:
Vendor-defined TPM Device Identifier.

Current Interpretation:
The TPM reports Device ID 0x{did:04X} ({did}).


[47:32] VID = 0x{vid:04X} ({vid})

Purpose:
Vendor Identifier assigned by the Trusted Computing Group (TCG).

Current Interpretation:
The TPM reports Vendor ID 0x{vid:04X} ({vid}), corresponding to {vendor_name}.


[31:24] RID = 0x{rid:02X} ({rid})

Purpose:
Vendor-defined TPM Revision Identifier.

Current Interpretation:
The TPM reports Revision ID 0x{rid:02X} ({rid}).


[23:22] CapSPICSUM = {checksum}

Purpose:
Reports checksum calculation capability.

Current Interpretation:
{checksum_text.get(checksum,"Reserved or vendor-defined capability.")}


[21:20] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[19] IntfSelLock = {lock}

Purpose:
Locks the InterfaceSelector field against further modification.

Current Interpretation:
{"The interface selection has been locked." if lock else "The interface selection remains configurable."}


[18:17] InterfaceSelector = {selector}

Purpose:
Indicates the selected TPM interface.

Current Interpretation:
{interface_selector.get(selector,"Reserved interface selector.")}


[16:15] CapIFRes

Purpose:
Reserved for future interface definitions.

Current Interpretation:
No interpretation is defined.


[14] CapCRB = {cap_crb}

Purpose:
Indicates CRB interface support.

Current Interpretation:
{"CRB interface is supported." if cap_crb else "CRB interface is not supported."}


[13] CapFIFO = {cap_fifo}

Purpose:
Indicates FIFO interface support.

Current Interpretation:
{"FIFO interface is supported." if cap_fifo else "FIFO interface is not supported."}


[12:11] CapDataXferSizeSupport = {transfer}

Purpose:
Reports the maximum CRB transfer size supported by the TPM.

Current Interpretation:
{transfer_text.get(transfer,"Reserved transfer capability.")}


[10] CapCRBChunk = {chunk}

Purpose:
Indicates support for CRB chunking.

Current Interpretation:
{"CRB chunking is supported." if chunk else "CRB chunking is not supported."}


[9] CapCRBIdleBypass = {idle_bypass}

Purpose:
Indicates support for bypassing the CRB Idle state.

Current Interpretation:
{"CRB Idle bypass is supported." if idle_bypass else "CRB Idle bypass is not supported."}


[8] CapLocality = {locality}

Purpose:
Reports supported TPM localities.

Current Interpretation:
{"The TPM supports Localities 0-4." if locality else "The TPM supports only Locality 0."}


[7:4] InterfaceVersion = {version}

Purpose:
Reports the implemented interface revision.

Current Interpretation:
The TPM reports Interface Version {version}.


[3:0] InterfaceType = {interface}

Purpose:
Identifies the currently active interface type.

Current Interpretation:
{interface_type.get(interface,"Reserved or vendor-defined interface type.")}

"""


    summary = f"""
The TPM identifies itself as a {vendor_name} device (Vendor ID 0x{vid:04X}, Device ID 0x{did:04X}, Revision ID 0x{rid:02X}). 
"""


    if cap_crb and cap_fifo:

        summary += """
Both the CRB and FIFO communication interfaces are supported.
"""

    elif cap_crb:

        summary += """
Only the CRB communication interface is reported as supported.
"""

    elif cap_fifo:

        summary += """
Only the FIFO communication interface is reported as supported.
"""

    else:

        summary += """
The current register values do not indicate support for either the CRB or FIFO communication interface.
"""


    summary += f"""
The active interface is reported as {interface_type.get(interface,'an implementation-defined interface').lower()} The maximum supported CRB transfer size is {transfer_text.get(transfer,'implementation-defined').lower()}
"""


    if chunk:

        summary += """
CRB chunked transfers are supported.
"""

    if idle_bypass:

        summary += """
CRB Idle bypass is supported, allowing faster transitions between TPM command phases.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : CTRL REQUEST
# ==========================================================

def decode_TPM_CRB_CTRL_REQ(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    idle = get_bit(value,1)

    ready = get_bit(value,0)


    description = f"""
TPM_CRB_CTRL_REQ Register

The TPM_CRB_CTRL_REQ register allows software to request TPM state transitions in the CRB interface. It is used to move the TPM between the Ready state and the Idle state before and after TPM command execution.

------------------------------------------------------------

[31:2] Reserved

Purpose:
Reserved by the TPM specification. Reads return 0 and writes are ignored.

Current Interpretation:
No interpretation is defined.


[1] goIdle = {idle}

Purpose:
Requests the TPM to transition from the Ready state back to the Idle state. Software typically sets this bit after the TPM response has been completely read. The TPM acknowledges completion by clearing this bit and updating the corresponding TPM_CRB_CTRL_STS.tpmIdle field.

Current Interpretation:
{"The host has requested the TPM to transition to the Idle state." if idle else "No request to transition the TPM to the Idle state has been issued."}


[0] cmdReady = {ready}

Purpose:
Requests the TPM to transition from the Idle state to the Ready state so that a new TPM command may be received. The TPM acknowledges completion by clearing this bit and updating the corresponding TPM_CRB_CTRL_STS.tpmIdle field.

Current Interpretation:
{"The host has requested the TPM to enter the Ready state and accept a new command." if ready else "No request to transition the TPM to the Ready state has been issued."}

"""


    #
    # Register Summary
    #

    if ready and idle:

        summary = """
The host requested multiple TPM state transitions by asserting both the Ready and Idle request bits. The TPM will acknowledge these requests by clearing the corresponding bits after the requested state transitions have completed.
"""

    elif ready:

        summary = """
The host requested that the TPM transition to the Ready state so that a new TPM command can be received through the CRB interface.
"""

    elif idle:

        summary = """
The host requested that the TPM transition to the Idle state after completion of TPM command processing and response retrieval.
"""

    else:

        summary = """
No TPM state transition request has been issued. The current register values do not indicate a request to enter either the Ready or the Idle state.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : CTRL STATUS
# ==========================================================

def decode_TPM_CRB_CTRL_STS(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    csum = get_bit(value,2)

    idle = get_bit(value,1)

    status = get_bit(value,0)


    description = f"""
TPM_CRB_CTRL_STS Register

The TPM_CRB_CTRL_STS register reports the current operational status of the TPM CRB interface. It indicates whether the TPM is currently idle, whether a command checksum is available, and whether the TPM is operating normally or has entered a fatal error state.

------------------------------------------------------------

[31:3] Reserved

Purpose:
Reserved by the TPM specification. Reads always return 0.

Current Interpretation:
No interpretation is defined.


[2] cSUMAvailable = {csum}

Purpose:
Indicates whether the command checksum is available for software to read through the TPM_DATA_CSUM register, provided checksum functionality is supported.

Current Interpretation:
{"The TPM has generated a command checksum, which is available for reading." if csum else "No command checksum is currently available."}


[1] tpmIdle = {idle}

Purpose:
Indicates whether the TPM is currently in the Idle state.

Current Interpretation:
{"The TPM is currently in the Idle state." if idle else "The TPM is not in the Idle state and may be processing or preparing to process a command."}


[0] tpmSts = {status}

Purpose:
Reports the overall operational status of the TPM.

Current Interpretation:
{"The TPM reports a fatal error condition." if status else "The TPM reports normal operation."}

"""


    #
    # Register Summary
    #

    if status:

        summary = """
The TPM reports a fatal error condition. The TPM is not operating normally and software intervention may be required before further TPM commands can be processed.
"""

    elif idle and csum:

        summary = """
The TPM is currently idle and has made a command checksum available for software to read. The TPM is operating normally.
"""

    elif idle:

        summary = """
The TPM is currently in the Idle state and is operating normally. No command checksum is currently available.
"""

    elif csum:

        summary = """
The TPM is operating normally and has made a command checksum available. The TPM is not currently in the Idle state.
"""

    else:

        summary = """
The TPM is operating normally. The current register values do not indicate that the TPM is idle or that a command checksum is currently available.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : CANCEL
# ==========================================================

def decode_TPM_CRB_CTRL_CANCEL(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_CANCEL Register

The TPM_CRB_CTRL_CANCEL register allows software to request cancellation of the currently executing TPM command. A value of 0x00000001 requests command cancellation, while a value of 0x00000000 indicates that no cancellation request is pending or that a previous cancellation request has been acknowledged.

------------------------------------------------------------

[31:0] Cancel = 0x{value:08X} ({value})

Purpose:
Controls TPM command cancellation. Writing a value of 0x00000001 requests cancellation of the currently executing TPM command. Once the TPM completes the cancellation process, this field returns to 0x00000000.

Current Interpretation:
{
"The host has requested cancellation of the currently executing TPM command."
if value == 1
else
"The TPM command cancellation field is cleared, indicating that no cancellation request is currently pending."
if value == 0
else
"The current register value is not defined by the TPM specification."
}

"""


    if value == 1:

        summary = """
The host requested cancellation of the currently executing TPM command. The TPM will acknowledge the request by clearing this register once the cancellation operation has completed.
"""

    elif value == 0:

        summary = """
No TPM command cancellation request is currently pending. The TPM is either executing normally or has already acknowledged a previous cancellation request.
"""

    else:

        summary = f"""
The TPM_CRB_CTRL_CANCEL register contains the value 0x{value:08X}. The current register value is not defined by the TPM specification and cannot be interpreted further.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : START
# ==========================================================

def decode_TPM_CRB_CTRL_START(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    chunk = get_bit(value,2)

    retry = get_bit(value,1)

    start = get_bit(value,0)


    description = f"""
TPM_CRB_CTRL_START Register

The TPM_CRB_CTRL_START register controls TPM command execution and command transfer through the CRB interface. It is used to start TPM command processing, manage chunked command transfers and request retransmission of TPM responses.

------------------------------------------------------------

[31:3] Reserved

Purpose:
Reserved by the TPM specification. Reads always return 0.

Current Interpretation:
No interpretation is defined.


[2] nextChunk = {chunk}

Purpose:
Controls chunked command transfer through the CRB Data Buffer.

During Command Reception:
Software sets this bit to indicate that another command chunk has been placed into the CRB Data Buffer. The TPM clears this bit after reading the chunk.

During Command Completion:
Software sets this bit to request the next response chunk from the TPM. The TPM clears this bit after placing the next response chunk into the CRB Data Buffer.

Current Interpretation:
{"The host has requested processing or transfer of the next CRB data chunk." if chunk else "No CRB chunk transfer request is currently pending."}


[1] crbRspRetry = {retry}

Purpose:
Requests retransmission of the first response chunk into the CRB Data Buffer. This is typically used when software wishes to receive the TPM response again.

Current Interpretation:
{"The host has requested retransmission of the TPM response." if retry else "No TPM response retransmission request is currently pending."}


[0] Start = {start}

Purpose:
Indicates that a TPM command placed in the CRB Data Buffer is ready for execution. The TPM clears this bit once command execution has begun and the interface transitions to Command Completion.

Current Interpretation:
{"The host has requested TPM command execution." if start else "No TPM command execution request is currently pending."}

"""


    #
    # Register Summary
    #

    actions = []

    if start:
        actions.append(
            "begin TPM command execution"
        )

    if retry:
        actions.append(
            "retransmit the TPM response"
        )

    if chunk:
        actions.append(
            "process or transfer the next CRB data chunk"
        )


    if len(actions) == 0:

        summary = """
No CRB control operation has been requested. The current register values do not indicate command execution, response retransmission or chunked data transfer.
"""

    elif len(actions) == 1:

        summary = f"""
The host requested the TPM to {actions[0]}.
"""

    else:

        summary = f"""
The host issued multiple CRB control operations, requesting the TPM to {', '.join(actions[:-1])} and {actions[-1]}.
"""


    return make_output(
        description,
        summary
    )
# ==========================================================
# CRB : INTERRUPT ENABLE
# ==========================================================

def decode_TPM_CRB_INT_ENABLE(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    global_int = get_bit(value,31)

    next_chunk = get_bit(value,4)

    locality = get_bit(value,3)

    establishment = get_bit(value,2)

    cmd_ready = get_bit(value,1)

    start = get_bit(value,0)


    description = f"""
TPM_CRB_INT_ENABLE Register

The TPM_CRB_INT_ENABLE register controls interrupt generation for the CRB interface. Individual interrupt sources may be enabled independently; however, interrupts are generated only when the Global Interrupt Enable bit is asserted.

------------------------------------------------------------

[31] globalInterruptEnable = {global_int}

Purpose:
Controls the global CRB interrupt enable. When cleared, all CRB interrupts are disabled regardless of the individual interrupt enable bits.

Current Interpretation:
{"Global CRB interrupt generation is enabled." if global_int else "Global CRB interrupt generation is disabled."}


[30:5] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[4] nextChunkCleared = {next_chunk}

Purpose:
Enables interrupt generation whenever the TPM clears the nextChunk control bit.

Current Interpretation:
{"Next Chunk Cleared interrupt generation is enabled." if next_chunk else "Next Chunk Cleared interrupt generation is disabled."}


[3] localityChangeIntEnable = {locality}

Purpose:
Enables interrupt generation whenever the active TPM locality changes.

Current Interpretation:
{"Locality Change interrupt generation is enabled." if locality else "Locality Change interrupt generation is disabled."}


[2] establishmentClearIntEnable = {establishment}

Purpose:
Enables interrupt generation whenever the TPM Establishment Flag is cleared.

Current Interpretation:
{"Establishment Clear interrupt generation is enabled." if establishment else "Establishment Clear interrupt generation is disabled."}


[1] cmdReadyIntEnable = {cmd_ready}

Purpose:
Enables interrupt generation whenever the TPM transitions to the Command Ready state.

Current Interpretation:
{"Command Ready interrupt generation is enabled." if cmd_ready else "Command Ready interrupt generation is disabled."}


[0] startIntEnable = {start}

Purpose:
Enables interrupt generation whenever command execution begins.

Current Interpretation:
{"Start interrupt generation is enabled." if start else "Start interrupt generation is disabled."}

"""


    #
    # Register Summary
    #

    if not global_int:

        summary = """
The CRB interrupt system is globally disabled. Although individual interrupt sources may be configured, no CRB interrupts will be generated while the Global Interrupt Enable bit remains cleared.
"""

    else:

        enabled = []

        if next_chunk:
            enabled.append("Next Chunk Cleared")

        if locality:
            enabled.append("Locality Change")

        if establishment:
            enabled.append("Establishment Clear")

        if cmd_ready:
            enabled.append("Command Ready")

        if start:
            enabled.append("Start")


        if len(enabled) == 0:

            summary = """
Global CRB interrupt generation is enabled; however, no individual interrupt sources are currently enabled. The current register values do not indicate that any CRB interrupt events will be generated.
"""

        elif len(enabled) == 1:

            summary = f"""
Global CRB interrupt generation is enabled. The TPM is configured to generate interrupts for the {enabled[0]} event.
"""

        else:

            summary = f"""
Global CRB interrupt generation is enabled. The TPM is configured to generate interrupts for the following events: {', '.join(enabled[:-1])} and {enabled[-1]}.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : INTERRUPT STATUS
# ==========================================================

def decode_TPM_CRB_INT_STS(
        payload,
        operation
    ):


    value = payload_to_int(payload)


    next_chunk = get_bit(value,4)

    locality = get_bit(value,3)

    establishment = get_bit(value,2)

    cmd_ready = get_bit(value,1)

    start = get_bit(value,0)


    description = ""


    if operation == "READ":


        description += f"""
TPM_CRB_INT_STS Register

The TPM_CRB_INT_STS register reports which CRB interrupt events have occurred. Individual interrupt status bits are asserted when their corresponding CRB events occur and remain asserted until cleared by software.

------------------------------------------------------------

[31:5] Reserved

Purpose:
Reserved by the TPM specification.

Current Interpretation:
No interpretation is defined.


[4] nextChunkClearedInt = {next_chunk}

Purpose:
Indicates that the TPM has cleared the nextChunk field and is ready for the next command or response chunk.

Current Interpretation:
{"A Next Chunk Cleared interrupt has occurred." if next_chunk else "No Next Chunk Cleared interrupt is currently reported."}


[3] localityChangeInt = {locality}

Purpose:
Indicates that the active TPM locality has changed.

Current Interpretation:
{"A Locality Change interrupt has occurred." if locality else "No Locality Change interrupt is currently reported."}


[2] establishmentClearInt = {establishment}

Purpose:
Indicates that the TPM Establishment Flag has been successfully cleared.

Current Interpretation:
{"An Establishment Clear interrupt has occurred." if establishment else "No Establishment Clear interrupt is currently reported."}


[1] cmdReadyInt = {cmd_ready}

Purpose:
Indicates that the TPM has successfully transitioned to the Ready state.

Current Interpretation:
{"A Command Ready interrupt has occurred." if cmd_ready else "No Command Ready interrupt is currently reported."}


[0] startInt = {start}

Purpose:
Indicates that TPM command execution has completed and the response is available for reading.

Current Interpretation:
{"A Start interrupt has occurred, indicating command completion or cancellation." if start else "No Start interrupt is currently reported."}

"""


        events = []

        if next_chunk:
            events.append("Next Chunk Cleared")

        if locality:
            events.append("Locality Change")

        if establishment:
            events.append("Establishment Clear")

        if cmd_ready:
            events.append("Command Ready")

        if start:
            events.append("Start")


        if len(events) == 0:

            summary = """
The TPM is not currently reporting any pending CRB interrupt events. The current register values do not indicate that any CRB interrupt conditions have occurred.
"""

        elif len(events) == 1:

            summary = f"""
The TPM reports a pending {events[0]} interrupt event.
"""

        else:

            summary = f"""
The TPM reports multiple pending CRB interrupt events, including {', '.join(events[:-1])} and {events[-1]}. These interrupt status flags remain asserted until cleared by software.
"""


    else:


        description += f"""
TPM_CRB_INT_STS Register

The TPM_CRB_INT_STS register allows software to acknowledge and clear CRB interrupt status flags. Writing a value of 1 to an interrupt status bit clears that interrupt, while writing 0 has no effect.

------------------------------------------------------------

[4] nextChunkClearedInt = {next_chunk}

Purpose:
Writing a value of 1 clears the Next Chunk Cleared interrupt.

Current Interpretation:
{"The host requested that the Next Chunk Cleared interrupt be cleared." if next_chunk else "The Next Chunk Cleared interrupt was not selected for clearing."}


[3] localityChangeInt = {locality}

Purpose:
Writing a value of 1 clears the Locality Change interrupt.

Current Interpretation:
{"The host requested that the Locality Change interrupt be cleared." if locality else "The Locality Change interrupt was not selected for clearing."}


[2] establishmentClearInt = {establishment}

Purpose:
Writing a value of 1 clears the Establishment Clear interrupt.

Current Interpretation:
{"The host requested that the Establishment Clear interrupt be cleared." if establishment else "The Establishment Clear interrupt was not selected for clearing."}


[1] cmdReadyInt = {cmd_ready}

Purpose:
Writing a value of 1 clears the Command Ready interrupt.

Current Interpretation:
{"The host requested that the Command Ready interrupt be cleared." if cmd_ready else "The Command Ready interrupt was not selected for clearing."}


[0] startInt = {start}

Purpose:
Writing a value of 1 clears the Start interrupt.

Current Interpretation:
{"The host requested that the Start interrupt be cleared." if start else "The Start interrupt was not selected for clearing."}

"""


        cleared = []

        if next_chunk:
            cleared.append("Next Chunk Cleared")

        if locality:
            cleared.append("Locality Change")

        if establishment:
            cleared.append("Establishment Clear")

        if cmd_ready:
            cleared.append("Command Ready")

        if start:
            cleared.append("Start")


        if len(cleared) == 0:

            summary = """
No CRB interrupt status flags were selected for clearing. The current register values do not indicate that any interrupt acknowledgement operation was requested.
"""

        elif len(cleared) == 1:

            summary = f"""
The host acknowledged and cleared the pending {cleared[0]} interrupt event.
"""

        else:

            summary = f"""
The host acknowledged and cleared multiple CRB interrupt events, including {', '.join(cleared[:-1])} and {cleared[-1]}.
"""


    return make_output(
        description,
        summary
    )

# ==========================================================
# CRB : COMMAND SIZE
# ==========================================================
def decode_TPM_CRB_CTRL_CMD_SIZE(
        payload,
        operation
    ):


    size = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_CMD_SIZE Register

The TPM_CRB_CTRL_CMD_SIZE register specifies the maximum size of the CRB Command Buffer. Software uses this value to determine the maximum TPM command that may be placed into the CRB command buffer without exceeding the implementation's supported buffer capacity.

------------------------------------------------------------

[31:0] commandSize = {size} bytes

Purpose:
Specifies the size, in bytes, of the TPM CRB Command Buffer. Software shall not construct TPM commands larger than this value when using the CRB interface.

Current Interpretation:
The TPM reports a maximum CRB command buffer size of {size} byte(s).
"""


    summary = f"""
The TPM reports that the CRB Command Buffer supports a maximum command size of {size} byte(s). TPM commands transferred through the CRB interface should not exceed this buffer capacity.
"""


    return make_output(
        description,
        summary
    )
# ==========================================================
# CRB : COMMAND LOW ADDRESS
# ==========================================================

def decode_TPM_CRB_CTRL_CMD_LADDR(
        payload,
        operation
    ):


    addr = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_CMD_LADDR Register

The TPM_CRB_CTRL_CMD_LADDR register contains the lower 32 bits of the physical base address of the CRB Command Buffer. Software uses this address to locate the memory region where TPM commands are written before command execution is requested.

------------------------------------------------------------

[31:0] Command Buffer Lower Address = 0x{addr:08X}

Purpose:
Specifies the lower 32 bits of the physical address of the CRB Command Buffer.

Current Interpretation:
The TPM reports the lower 32 bits of the Command Buffer physical address as 0x{addr:08X}. This address forms the base of the memory region used to transfer TPM commands through the CRB interface.
"""


    summary = f"""
The TPM reports the lower 32 bits of the CRB Command Buffer physical address as 0x{addr:08X}. Software uses this address together with the upper address register, when present, to locate the command buffer in system memory.
"""


    return make_output(
        description,
        summary
    )
# ==========================================================
# CRB : COMMAND HIGH ADDRESS
# ==========================================================

def decode_TPM_CRB_CTRL_CMD_HADDR(
        payload,
        operation
    ):


    addr = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_CMD_HADDR Register

The TPM_CRB_CTRL_CMD_HADDR register contains the upper 32 bits of the physical base address of the CRB Command Buffer. Together with the TPM_CRB_CTRL_CMD_LADDR register, it forms the complete 64-bit physical address of the memory region used for TPM command transfers.

------------------------------------------------------------

[31:0] Command Buffer Upper Address = 0x{addr:08X}

Purpose:
Specifies the upper 32 bits of the physical address of the CRB Command Buffer.

Current Interpretation:
The TPM reports the upper 32 bits of the Command Buffer physical address as 0x{addr:08X}. This value should be combined with the lower address register to obtain the complete 64-bit physical address of the CRB Command Buffer.
"""


    summary = f"""
The TPM reports the upper 32 bits of the CRB Command Buffer physical address as 0x{addr:08X}. This value should be combined with the corresponding lower address register to determine the complete 64-bit physical address of the command buffer.
"""


    return make_output(
        description,
        summary
    )


# ==========================================================
# CRB : RESPONSE SIZE
# ==========================================================
def decode_TPM_CRB_CTRL_RSP_SIZE(
        payload,
        operation
    ):


    size = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_RSP_SIZE Register

The TPM_CRB_CTRL_RSP_SIZE register specifies the maximum size of the CRB Response Buffer. Software uses this value to determine the maximum TPM response that may be returned through the CRB interface without exceeding the implementation's supported response buffer capacity.

------------------------------------------------------------

[31:0] Response Buffer Size = {size} byte(s)

Purpose:
Specifies the size, in bytes, of the TPM CRB Response Buffer. TPM responses returned by the TPM shall not exceed this buffer capacity when using the CRB interface.

Current Interpretation:
The TPM reports a maximum CRB response buffer size of {size} byte(s).
"""


    summary = f"""
The TPM reports that the CRB Response Buffer supports a maximum response size of {size} byte(s). TPM responses returned through the CRB interface should not exceed this buffer capacity.
"""


    return make_output(
        description,
        summary
    )


# ==========================================================
# CRB : RESPONSE ADDRESS
# ==========================================================

def decode_TPM_CRB_CTRL_RSP_ADDR(
        payload,
        operation
    ):


    addr = payload_to_int(payload)


    description = f"""
TPM_CRB_CTRL_RSP_ADDR Register

The TPM_CRB_CTRL_RSP_ADDR register contains the physical base address of the CRB Response Buffer. After TPM command execution completes, the TPM writes the generated response into this memory region, from which software subsequently retrieves the response.

------------------------------------------------------------

[31:0] Response Buffer Address = 0x{addr:08X}

Purpose:
Specifies the physical base address of the CRB Response Buffer used to store TPM responses.

Current Interpretation:
The TPM reports the Response Buffer physical address as 0x{addr:08X}. TPM responses generated through the CRB interface are written to this memory location.
"""


    summary = f"""
The TPM reports the CRB Response Buffer physical address as 0x{addr:08X}. TPM responses generated by the device are written to this memory region, from which software may subsequently retrieve the response.
"""


    return make_output(
        description,
        summary
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