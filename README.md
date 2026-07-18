

<h3 align="center">
TPM 2.0 Transaction Analysis Framework
</h3>

<p align="center">
Reconstruct • Decode • Analyze • Visualize
</p>

---

**TPM-Scope** is a desktop application for reconstructing, decoding, and analyzing TPM 2.0 transactions.

It converts raw TPM communication captures into human-readable TPM operations by reconstructing transactions, decoding TPM registers, interpreting TPM commands and responses, and analyzing measured boot events.

TPM-Scope is designed to work completely offline and requires no external software installation.

---

## Features

- TPM 2.0 SPI transaction reconstruction
- FIFO and CRB interface support
- TPM register decoding
- TPM command and response decoding
- Interactive Transaction Browser
- Single transaction inspection
- Batch CSV analysis
- PCR Extend summary generation
- TPM command summary generation
- Cross-platform desktop application
- Fully offline operation

---

## Supported Platforms

- Windows (64-bit)
- Linux (64-bit)

---

## Downloads

Pre-built binaries are available from the **Releases** page.

Available packages include:

- Windows Portable Executable (`.exe`)
- Linux AppImage
- Linux Portable Archive (`.tar.gz`)
- Source Code (`.7z`)

---

## Running TPM-Scope

### Windows

Run the executable:

```text
TPM-Scope.exe
```

No installation is required.

### Linux

Make the AppImage executable:

```bash
chmod +x TPM-Scope.AppImage
./TPM-Scope.AppImage
```

Alternatively, extract and run the provided `tar.gz` package.

---

## Building from Source

Clone the repository:

```bash
git clone https://github.com/arushmangalambajpai/TPM-Scope.git

cd TPM-Scope
```

Install dependencies:

```bash
cd app

npm install
```

Start the application:

```bash
npm start
```

---

## Input

TPM-Scope accepts TPM SPI captures exported as CSV files.

The application reconstructs TPM transactions and generates decoded outputs for further analysis.

---

## Generated Outputs

Depending on the selected analysis mode, TPM-Scope can generate:

- `clean_spi_transactions.csv`
- `decoded_transactions.csv`
- `tpm_command_summary.txt`
- `pcr_extend_summary.txt`

---

## Project Structure

```text
TPM-Scope/

├── app/                     # Electron application
├── web/                     # Frontend assets
├── spi_stream/              # TPM decoding engine
├── transaction_builder.py
├── transaction_csv_decoder.py
├── tpm_command_summary.py
├── pcr_extend_summaries.py
├── LICENSE
└── README.md
```

---

## Third-Party Software

TPM-Scope incorporates **TPMStream** for TPM command parsing and TPM structure representation.

Original Author:

- Johannes Holland

License:

- BSD 2-Clause License

The original license is included in this repository.

---

## License

This project is licensed under the **BSD 2-Clause License**.

See the `LICENSE` file for details.

---

## Author

**Arush Mangalam Bajpai**

Engineering Project developed at the **Scientific Analysis Group (SAG), Defence Research and Development Organisation (DRDO)**.
