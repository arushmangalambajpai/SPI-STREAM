import csv
import os
import sys

# ==========================================================
# Existing SPI decoder path injection
# ==========================================================
sys.path.append(os.path.join(os.getcwd(), "spi_stream"))

from spi_header_decoder import convert_spi_to_stream_arr

OUTPUT_FILE = "clean_spi_transactions.csv"

# ==========================================================
# Transformation Helpers
# ==========================================================

def clean_byte(x):
    if x is None:
        return None
    x = x.strip()
    if x == "":
        return None
    return x.replace("0x", "").replace("0X", "").upper().zfill(2)

def to_int(data):
    return [int(x, 16) for x in data]

def to_hex(data):
    return [f"{x:02X}" for x in data]

def is_buffer_register(addr):
    """
    Checks if target address belongs to a Data FIFO register 
    or a CRB Command/Response data buffer region.
    Excludes fixed configuration registers starting at 0x0F00 (like DID_VID).
    """
    # FIFO Data Registers: 0x0024 - 0x0027
    # CRB Data Buffer Range: 0x0080 up to 0x0EFF
    return (0x024 <= addr <= 0x027) or (0x080 <= addr <= 0x0EFF)

# ==========================================================
# CSV Input Parser & Grouping Engine
# ==========================================================

def build_transactions(input_file):
    transactions = []
    current = None

    with open(input_file, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            idx = row.get("Index", "").strip()

            if idx:
                if current:
                    transactions.append(current)
                current = {
                    "index": idx,
                    "mosi": [],
                    "miso": []
                }

            if current is None:
                continue

            mosi = clean_byte(row.get("MOSI"))
            miso = clean_byte(row.get("MISO"))

            if mosi:
                current["mosi"].append(mosi)
            if miso:
                current["miso"].append(miso)

        if current:
            transactions.append(current)

    return transactions

# ==========================================================
# Core Processing Pipeline
# ==========================================================

def process(transactions):
    output = []
    
    # Failure Tracking Registries
    decode_fails = []
    incomplete_fails = []
    
    # Success Tracking Groups
    cleaned_groups = []

    # MOSI Accumulator States (Writes)
    mosi_buffer = []
    mosi_expected_size = None
    mosi_contributors = []

    # MISO Accumulator States (Reads)
    miso_buffer = []
    miso_expected_size = None
    miso_contributors = []

    TPM_TAGS = [[0x80, 0x01], [0x80, 0x02], [0xC0, 0x01], [0xC0, 0x02]]

    for t in transactions:
        mosi_str = " ".join(t["mosi"])

        try:
            (
                interface,
                op_header,
                operation,
                byte_length,
                locality,
                register_addr,
                payload
            ) = convert_spi_to_stream_arr("FIFO", mosi_str)

            b_len = int(byte_length)
            addr = int(register_addr, 16)
        except Exception:
            # FAILURE CASE 1: Header is corrupted or unparsable
            decode_fails.append(f"(Index: {t['index']})")
            output.append(t)
            continue

        # Isolate target data stream payload bytes (skipping the 4-byte SPI header)
        current_payload_bytes = t["mosi"][4:] if operation == "WRITE" else t["miso"][4:]

        # VALIDATION RULE: Payload must contain the expected bytelength
        if len(current_payload_bytes) < b_len:
            # FAILURE CASE 2: Transaction was cut off or incomplete
            fail_msg = f"({t['index']}, {len(current_payload_bytes)} / {b_len}, {register_addr})"
            incomplete_fails.append(fail_msg)
            output.append(t)
            continue

        # ROUTING RULE: Differentiate based on Register Type
        if not is_buffer_register(addr):
            # Direct generation for non-buffer registers (Fixes Index 1)
            clean_t = {
                "index": t["index"],
                "mosi": t["mosi"][:4] + (t["mosi"][4:] if operation == "WRITE" else ["00"] * len(t["mosi"][4:])),
                "miso": t["miso"][:4] + (t["miso"][4:] if operation == "READ" else ["00"] * len(t["miso"][4:]))
            }
            output.append(clean_t)
        else:
            # Buffer accumulation path (FIFO / CRB data lines)
            int_payload = to_int(current_payload_bytes)

            if operation == "WRITE":
                mosi_buffer.extend(int_payload)
                mosi_contributors.append(str(t["index"]))

                # Dynamic Tag Scanning: Locate packet structure boundaries
                tag_idx = -1
                for i in range(len(mosi_buffer) - 1):
                    if mosi_buffer[i:i+2] in TPM_TAGS:
                        tag_idx = i
                        break

                # Extract size fields once 6 bytes of the valid packet are collected
                if tag_idx != -1 and mosi_expected_size is None:
                    if len(mosi_buffer) >= tag_idx + 6:
                        mosi_expected_size = int.from_bytes(bytes(mosi_buffer[tag_idx+2 : tag_idx+6]), "big")

                # Emit when target packet size criterion is fully satisfied
                if mosi_expected_size is not None and len(mosi_buffer[tag_idx:]) >= mosi_expected_size:
                    total_payload_len = len(mosi_buffer)
                    
                    clean_t = {
                        "index": t["index"],  # Tied to the final contributing index
                        "mosi": t["mosi"][:4] + to_hex(mosi_buffer), 
                        "miso": t["miso"][:4] + ["00"] * total_payload_len 
                    }
                    output.append(clean_t)
                    cleaned_groups.append(f"({','.join(mosi_contributors)})")

                    # Slide buffer window past processed data packet bounds
                    mosi_buffer = mosi_buffer[tag_idx + mosi_expected_size:]
                    mosi_expected_size = None
                    mosi_contributors = []

            elif operation == "READ":
                miso_buffer.extend(int_payload)
                miso_contributors.append(str(t["index"]))

                # Dynamic Tag Scanning for Read Responses
                tag_idx = -1
                for i in range(len(miso_buffer) - 1):
                    if miso_buffer[i:i+2] in TPM_TAGS:
                        tag_idx = i
                        break

                if tag_idx != -1 and miso_expected_size is None:
                    if len(miso_buffer) >= tag_idx + 6:
                        miso_expected_size = int.from_bytes(bytes(miso_buffer[tag_idx+2 : tag_idx+6]), "big")

                if miso_expected_size is not None and len(miso_buffer[tag_idx:]) >= miso_expected_size:
                    total_payload_len = len(miso_buffer)

                    clean_t = {
                        "index": t["index"],
                        "mosi": t["mosi"][:4] + ["00"] * total_payload_len, 
                        "miso": t["miso"][:4] + to_hex(miso_buffer) 
                    }
                    output.append(clean_t)
                    cleaned_groups.append(f"({','.join(miso_contributors)})")

                    # Slide buffer window past processed data packet bounds
                    miso_buffer = miso_buffer[tag_idx + miso_expected_size:]
                    miso_expected_size = None
                    miso_contributors = []

    # Print out precise pipeline notifications directly to stdout
    if decode_fails:
        print("Header Decode Failures: " + ", ".join(decode_fails))
    if incomplete_fails:
        print("Incomplete Transaction " + ", ".join(incomplete_fails) + ".")
    if cleaned_groups:
        print("Generated Clean Transactions " + " , ".join(cleaned_groups))

    return output

# ==========================================================
# Data Destination Writer
# ==========================================================

def save(data):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Length", "MOSI", "MISO"])

        for t in data:
            writer.writerow([
                t["index"],
                len(t["mosi"]),
                " ".join(t["mosi"]),
                " ".join(t["miso"])
            ])

# ==========================================================
# Execution Core
# ==========================================================

def main(input_file):
    raw = build_transactions(input_file)
    clean = process(raw)
    save(clean)

    print("\n" + "=" * 60)
    print("TRANSACTION BUILDER PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Number of input transactions        : {len(raw)}")
    print(f"Final number of cleaned transactions: {len(clean)}")
    print(f"Output saved to                     : {OUTPUT_FILE}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main("rpi_boot_csv.csv")