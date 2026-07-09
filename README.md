# SPI-STREAM

**SPI-STREAM** is a TPM 2.0 SPI transaction reconstruction and analysis framework.

It converts raw TPM SPI bus captures into meaningful TPM operations by rebuilding transactions, decoding TPM registers, parsing TPM commands/responses, and extracting measured boot events.

SPI-STREAM provides:

- A Python terminal analyzer
- A browser-based Web Analyzer powered by Pyodide

## Try SPI-STREAM Online

The complete analyzer is available directly through GitHub Pages:

```text
https://arushmangalambajpai.github.io/SPI-STREAM/web/

```

## Overview

No installation required.

The Web Analyzer:

Runs the complete Python decoder engine in the browser
Uses Pyodide (Python compiled to WebAssembly)
Requires no backend server
Does not upload TPM logs anywhere
Works on Windows, Linux, and macOS browsers

Your TPM traces remain completely local.

Modern TPM devices communicate with the host through interfaces such as SPI.
Raw SPI captures contain byte streams that are difficult to interpret manually.

SPI-STREAM transforms these captures into structured TPM information.

Pipeline:

```text
Raw TPM SPI Capture
          |
          v
SPI Transaction Builder
          |
          v
Clean MOSI/MISO Streams
          |
          v
FIFO / CRB Transport Decoder
          |
          v
TPM Command Decoder
          |
          v
TPM SPI Decoder Engine
          |
     +----+----+
     |         |
     v         v
    CLI     Web Analyzer
```



## Features

### SPI Transaction Layer

- Raw SPI CSV parsing
- MOSI/MISO stream reconstruction
- TPM SPI header decoding
- FIFO transaction analysis
- CRB transaction analysis
- Fragmented TPM command handling
- TPM response reconstruction

---

### TPM Interface and Register Decoder

SPI-STREAM supports both major TPM 2.0 interfaces:

- FIFO (First-In First-Out Interface)
- CRB (Command Response Buffer Interface)

The decoder automatically interprets TPM transport structures and register accesses.

Examples:

- TPM_ACCESS
- TPM_STS
- TPM_DATA_FIFO
- TPM_INTERFACE_ID
- TPM_DID_VID

Decoded fields include:

- Operation direction
- Locality
- Register address
- Payload bytes
- Register meaning

---

### TPM Command Decoder

SPI-STREAM detects and decodes TPM commands including:

- TPM2_Startup
- TPM2_GetRandom
- TPM2_PCR_Read
- TPM2_PCR_Extend

Output includes:

- TPM command tag
- Command size
- Command code
- Command name
- Command payload

---

### TPM Response Decoder

TPM responses are reconstructed and decoded into:

- Response tag
- Response size
- Response code
- Response payload

---

### PCR Extend Analyzer

SPI-STREAM can extract measured boot PCR extensions.

Generated information:

- Transaction index
- PCR index
- Digest algorithm
- Digest values
- Boot measurement timeline

---

# Interfaces

## 1. Command Line Interface

The CLI provides an interactive terminal analyzer.

Features:

- Decode single SPI transactions
- Generate decoded CSV files
- View TPM command summaries
- Analyze PCR Extend operations

---

## 2. Web Analyzer

SPI-STREAM includes a browser version using:

- HTML
- CSS
- JavaScript
- Pyodide

Architecture:

```text
Browser
   |
   v
Pyodide WebAssembly Python
   |
   v
SPI-STREAM Decoder Engine
```

Advantages:

- No backend
- No installation
- Works on GitHub Pages
- Runs fully offline after loading
- TPM traces stay inside the browser

---

# Installation

## Clone Repository

```bash
git clone https://github.com/arushmangalambajpai/SPI-STREAM.git

cd SPI-STREAM
```

---

## Create Python Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# CLI Usage

Run:

```bash
python -m spi_stream_cli
```

The interactive menu provides:

```text
1. Get SPI Transactions

2. Generate decoded_transactions.csv

3. Decode one transaction

4. TPM Command Summary

5. PCR Extend Summary
```

---

# Web Usage

Start a local static server:

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/web/
```

The official SPI-STREAM Web Analyzer is hosted using GitHub Pages:

```text
https://arushmangalambajpai.github.io/SPI-STREAM/web/
---
It runs the same decoder engine used by the CLI through Pyodide.

# Input CSV Format

SPI-STREAM expects SPI captures exported as CSV.

The format is based on SPI analyzer exports.

Required columns:

| Column | Description |
|---|---|
| Index | SPI transaction/frame index |
| TIME STAMP | Capture timestamp |
| FRAME TYPE | Analyzer frame type |
| PACKET INFO | Analyzer metadata |
| START | Transaction start marker |
| MOSI | Master Out Slave In byte |
| MISO | Master In Slave Out byte |
| STOP | Transaction stop marker |
| ERROR | SPI analyzer error flag |
| FREQUENCY | SPI clock frequency |

Example:

```csv
Index,TIME STAMP,FRAME TYPE,PACKET INFO,START,MISO,MOSI,STOP,ERROR,FREQUENCY
1,0.000001,DATA,,,00,80,,,
,,DATA,,,00,D4,,,
,,DATA,,,00,00,,,
,,DATA,,,00,18,,,
```

SPI bytes belonging to the same transfer may span multiple CSV rows.

---

# Generated Files

## clean_spi_transactions.csv

Generated by:

```text
transaction_builder.py
```

Contains reconstructed complete SPI transfers.

Format:

```csv
Index,Length,MOSI,MISO
```

---

## decoded_transactions.csv

Generated by:

```text
transaction_csv_decoder.py
```

Contains:

- Stream direction
- Operation type
- Register information
- TPM command information
- TPM response information

---

## tpm_command_summary.txt

Generated by:

```text
tpm_command_summary.py
```

Contains:

- Unique TPM commands
- Command frequency
- Transaction indexes

---

## pcr_extend_summary.txt

Generated by:

```text
pcr_extend_summaries.py
```

Contains:

- PCR Extend timeline
- PCR indexes
- Hash algorithms
- Digest values

---

# Project Structure

```text
SPI-STREAM/

├── spi_stream/
│
│   ├── decode_spi.py
│   ├── spi_header_decoder.py
│   ├── register_decoder.py
│   ├── tpm_command_decoder.py
│   ├── tpm_response_decoder.py
│   ├── pcr_extend_decoder.py
│   │
│   └── tpmstream/
│
├── spi_stream_cli/
│
├── web/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── python/
│
├── transaction_builder.py
├── transaction_csv_decoder.py
├── tpm_command_summary.py
├── pcr_extend_summaries.py
│
├── README.md
├── LICENSE
└── NOTICE
```

---

# Third Party Credits

## TPMStream

SPI-STREAM uses TPMStream for TPM command object parsing and TPM structure representation.

Original author:

**Johannes Holland**

Copyright:

```
Copyright (c) 2022, Johannes Holland
All rights reserved.
```

TPMStream is distributed under the BSD 2-Clause License.

The original license is preserved with the included TPMStream source.

SPI-STREAM adds:

- SPI reconstruction
- Register decoding
- Command analysis pipeline
- CLI interface
- Browser-based Pyodide frontend

around TPMStream.

---

# License

SPI-STREAM is released under the **BSD 2-Clause License**.

See:

```text
LICENSE
```

for details.

---

# Author

Created by:

**Arush Mangalam Bajpai**

For TPM 2.0, measured boot, and embedded security analysis research.
