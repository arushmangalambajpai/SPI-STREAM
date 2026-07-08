"""
TPM Response Decoder

Wrapper around tpmstream.

Unlike commands, TPM responses need the
original command code to decode parameters.

Input:

response bytes
+
command_code


Output:

{
    tag,
    response_size,
    response_code,
    response_name,
    tree
}


Used later by:

MISO_TPM object
"""


# ==========================================================
# IMPORT TPMSTREAM
# ==========================================================


try:


    from tpmstream.io.auto import Auto

    from tpmstream.io.pretty import Pretty

    from tpmstream.common.object import events_to_objs

    from tpmstream.spec.commands import Response

    from tpmstream.spec.structures.constants import TPM_CC


    TPMSTREAM_AVAILABLE = True



except Exception:


    TPMSTREAM_AVAILABLE = False





# ==========================================================
# BYTE CONVERSION
# ==========================================================


def payload_to_bytes(payload):


    if isinstance(payload, list):

        hex_string = "".join(payload)


    else:

        hex_string = payload.replace(
            " ",
            ""
        )


    return bytes.fromhex(
        hex_string
    )





# ==========================================================
# COMMAND CODE CONVERSION
# ==========================================================


def normalize_command_code(command_code):


    if not TPMSTREAM_AVAILABLE:


        return command_code



    try:


        if isinstance(command_code, TPM_CC):


            return command_code



        text = str(command_code)



        # Example:
        #
        # TPM_CC.PCR_Extend
        #        |
        #        v
        # PCR_Extend


        if "." in text:


            name = text.split(".")[-1]


            if hasattr(TPM_CC, name):


                return getattr(
                    TPM_CC,
                    name
                )



        # raw hex support


        if text.startswith("0x"):


            value = int(
                text,
                16
            )


        else:


            value = int(
                text,
                16
            )



        return TPM_CC(
            value
        )



    except Exception:


        return command_code




# ==========================================================
# FALLBACK HEADER DECODER
# ==========================================================


def manual_response_header_decode(payload):


    data = payload_to_bytes(
        payload
    )


    if len(data) < 10:


        return {

            "tag":None,

            "response_size":None,

            "response_code":None,

            "response_name":"INVALID_RESPONSE"

        }



    tag = int.from_bytes(
        data[0:2],
        "big"
    )


    size = int.from_bytes(
        data[2:6],
        "big"
    )


    code = int.from_bytes(
        data[6:10],
        "big"
    )



    name = (

        "SUCCESS"

        if code == 0

        else

        "TPM_ERROR"

    )



    return {

        "tag":hex(tag),

        "response_size":size,

        "response_code":hex(code),

        "response_name":name

    }






# ==========================================================
# TREE DECODER
# ==========================================================


def get_tpmstream_tree(
        payload,
        command_code
    ):


    if not TPMSTREAM_AVAILABLE:


        return "tpmstream unavailable"



    try:


        data = payload_to_bytes(
            payload
        )


        cc = normalize_command_code(
            command_code
        )



        events = Auto.marshal(

            tpm_type = Response,

            buffer = data,

            command_code = cc,

            abort_on_error = False

        )



        generator = Pretty.unmarshal(
            events
        )


        tree = ""


        for line in generator:

            tree += str(line)

            tree += "\n"



        return tree



    except Exception as e:


        return (

            "Unable to generate TPM response tree: "

            +

            str(e)

        )





# ==========================================================
# MAIN RESPONSE DECODER
# ==========================================================


def decode_tpm_response(
        payload,
        command_code
    ):


    output = manual_response_header_decode(
        payload
    )



    output["tree"] = get_tpmstream_tree(

        payload,

        command_code

    )



    if not TPMSTREAM_AVAILABLE:


        return output




    try:


        data = payload_to_bytes(
            payload
        )


        cc = normalize_command_code(
            command_code
        )



        events = Auto.marshal(

            tpm_type = Response,

            buffer = data,

            command_code = cc,

            abort_on_error = False

        )



        objects = list(
            events_to_objs(events)
        )


        response = objects[0]



        output["tag"] = str(

            response.tag

        )



        output["response_size"] = int(

            response.responseSize

        )



        output["response_code"] = str(

            response.responseCode

        )



        name = str(

            response.responseCode

        )


        if "." in name:

            name = name.split(".")[-1]



        output["response_name"] = name




    except Exception:


        pass



    return output






# ==========================================================
# SELF TEST
# ==========================================================


if __name__ == "__main__":


    print(

        "\nTPM RESPONSE DECODER TEST\n"

    )



    tests = {


        "Startup SUCCESS":

        (

        "TPM_CC.Startup",

        [

            "80","01",

            "00","00","00","0A",

            "00","00","00","00"

        ]

        ),

        "GetCapability SUCCESS":

        (

        "TPM_CC.GetCapability",

        [

            # TPM_ST_NO_SESSIONS

            "80","01",



           # size = 27 bytes

            "00","00","00","1B",



            # TPM_RC_SUCCESS

            "00","00","00","00",



            # moreData

            "00",



            # TPMS_CAPABILITY_DATA


            # capability
            # TPM_CAP_TPM_PROPERTIES

            "00","00","00","06",



            # TPML_TAGGED_TPM_PROPERTY


            # count = 1

            "00","00","00","01",



            # TPM_PT_MANUFACTURER

            "00","00","01","05",



            # value
            # example IFX = 0x49465800

            "49","46","58","00"

        ]

        ),

        "PCR_Extend SUCCESS":

        (
        
        "TPM_CC.PCR_Extend",

        [
        
            # TPM_ST_SESSIONS

            "80","02",


            # response size = 19 bytes

            "00","00","00","13",


            # TPM_RC_SUCCESS

            "00","00","00","00",


            # parameter size = 0

            "00","00","00","00",


            # authorization response


            # nonce size = 0

            "00","00",


            # session attributes

            "00",


            # hmac size = 0

            "00","00"

        ]

        ),



        "GetRandom SUCCESS":

        (

        "TPM_CC.GetRandom",

        [

            "80","01",

            "00","00","00","1C",

            "00","00","00","00",


            # TPM2B_DIGEST size

            "00","10",


            # random bytes

            "11","22","33","44",

            "55","66","77","88",

            "99","AA","BB","CC",

            "DD","EE","FF","00"

        ]

        ),



        "ERROR RESPONSE":

        (

        "TPM_CC.Startup",

        [

            "80","01",

            "00","00","00","0A",

            "00","00","01","01"

        ]

        )

    }





    for name,(cmd,response) in tests.items():


        print(
            "\n=============================="
        )


        print(name)


        print(
            "=============================="
        )



        result = decode_tpm_response(

            response,

            cmd

        )



        print(
            "TAG:",
            result["tag"]
        )


        print(
            "SIZE:",
            result["response_size"]
        )


        print(
            "CODE:",
            result["response_code"]
        )


        print(
            "NAME:",
            result["response_name"]
        )



        print(
            "\nTREE:\n"
        )


        print(
            result["tree"]
        )




    print(

        "\nALL RESPONSE TESTS COMPLETE\n"

    )