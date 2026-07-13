
        // Initialize Icons
        lucide.createIcons();

        // Application State
        let pyodideInstance = null;
        let isPyodideReady = false;
        let currentMode = 'MOSI';
        let explorerTransactions = [];
        let selectedExplorerRow = null;
        

        
        
        // ==========================================
        // UI INTERACTION LOGIC
        // ==========================================

        function switchTab(tab) {
            // View Switching
            document.getElementById('view-single').classList.toggle('hidden', tab !== 'single');
            document.getElementById('view-csv').classList.toggle('hidden', tab !== 'csv');
            
            // Tab Styling Updates
            const btnSingle = document.getElementById('tab-single');
            const btnCsv = document.getElementById('tab-csv');
            
            const activeClasses = 'flex-1 py-1.5 text-xs font-semibold rounded-md bg-base-700 text-white shadow-sm transition-all';
            const inactiveClasses = 'flex-1 py-1.5 text-xs font-semibold rounded-md text-gray-400 hover:text-gray-200 transition-all bg-transparent';

            if (tab === 'single') {
                btnSingle.className = activeClasses;
                btnCsv.className = inactiveClasses;
            } else {
                btnCsv.className = activeClasses;
                btnSingle.className = inactiveClasses;
            }
            
            clearTerminal();
            appendToTerminal(`[SYS] Switched context to ${tab === 'single' ? 'Single Transaction Decode' : 'Batch CSV Analysis'}.`, "system");
        }

        function toggleMisoInput() {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            currentMode = mode;
            const container = document.getElementById('miso-container');
            
            const inputs = document.querySelectorAll('input[name="mode"]');
            const mosiLabel = inputs[0].parentNode;
            const fullLabel = inputs[1].parentNode;

            const activeClass = 'flex-1 text-center py-1.5 rounded bg-base-700 text-white text-xs font-medium cursor-pointer transition-all';
            const inactiveClass = 'flex-1 text-center py-1.5 rounded text-gray-400 hover:text-white text-xs font-medium cursor-pointer transition-all bg-transparent';

            if (mode === 'FULL') {
                container.classList.remove('hidden');
                fullLabel.className = activeClass;
                mosiLabel.className = inactiveClass;
            } else {
                container.classList.add('hidden');
                mosiLabel.className = activeClass;
                fullLabel.className = inactiveClass;
            }
        }

        // Handle styling for Interface toggle (FIFO/CRB)
        document.querySelectorAll('input[name="interface"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const activeClass = 'flex-1 text-center py-1.5 rounded bg-base-700 text-white text-xs font-medium cursor-pointer transition-all';
                const inactiveClass = 'flex-1 text-center py-1.5 rounded text-gray-400 hover:text-white text-xs font-medium cursor-pointer transition-all bg-transparent';
                
                document.querySelectorAll('input[name="interface"]').forEach(r => {
                    r.parentNode.className = r.checked ? activeClass : inactiveClass;
                });
            });
        });

        // Appends text specifically styled for the giant terminal
        function appendToTerminal(text, type = 'normal') {
            const terminal = document.getElementById('terminal-output');
            const span = document.createElement('span');
            
            if (type === 'error') span.className = 'text-terminal-error';
            else if (type === 'system') span.className = 'text-terminal-system font-semibold';
            else if (type === 'success') span.className = 'text-terminal-success';
            else span.className = 'text-gray-300'; // Default text color
            
            span.textContent = text + '\n';
            terminal.appendChild(span);
            
            // Auto-scroll the container
            const container = terminal.parentElement;
            container.scrollTop = container.scrollHeight;
        }

        function clearTerminal() {
            document.getElementById('terminal-output').innerHTML = '';
        }
        
        // ==========================================
        // PYODIDE & PYTHON BRIDGE LOGIC
        // ==========================================

        async function initPyodideEngine() {
            try {
                const statusBadge = document.getElementById('engine-status');
                const statusIcon = statusBadge.querySelector('i');
                const statusText = document.getElementById('engine-status-text');
                
                pyodideInstance = await loadPyodide();
                            
                await pyodideInstance.loadPackage(
                    "micropip"
                );


                const micropip =
                pyodideInstance.pyimport(
                    "micropip"
                );


                await micropip.install(
                    "dpkt",
                    "colorama"
                );   
                
                appendToTerminal(
                
                    "[SYS] Loading TPM-SCOPE package...",
                
                    "system"
                
                );






                
                let response =
                
                await fetch(
                
                    "python/spi_stream.zip"
                
                );




                
                let zipBuffer =
                
                await response.arrayBuffer();






                
                pyodideInstance.FS.writeFile(
                

                
                    "spi_stream.zip",
                

                
                    new Uint8Array(
                
                        zipBuffer
                
                    )
                

                
                );
                let check =
                await pyodideInstance.runPythonAsync(`
                
                import os
                
                "FILES: " + str(os.listdir("."))
                
                `);
                
                
                appendToTerminal(
                    check,
                    "system"
                );






                
                await pyodideInstance.runPythonAsync(`
                import zipfile
                
                with zipfile.ZipFile("spi_stream.zip") as z:
                    z.extractall(".")
                
                print("SPI STREAM extracted")
                `);

                statusText.textContent = "Loading SPI Engine";
                            
                            
                appendToTerminal(
                    "[SYS] Pyodide loaded",
                    "system"
                );
                
                
                
                
                await pyodideInstance.runPythonAsync(`
                import sys
                
                
                sys.path.insert(
                    0,
                    "spi_stream"
                )
                
                
                sys.path.insert(
                    0,
                    "spi_stream/tpmstream/src"
                )
                
                
                
                
                
                from decode_spi import (
                    decode_mosi,
                    decode_transaction
                )
                # Patch TPMStream Pretty renderer for browser

                import importlib


                pretty_module = importlib.import_module(
                    "tpmstream.io.pretty.unmarshal"
                )


                for name in [

                    "BLACK",
                    "BLUE",
                    "YELLOW",
                    "RED",
                    "GREEN",
                    "CYAN",
                    "MAGENTA",
                    "WHITE",
                    "LIGHTGREEN_EX"

                ]:

                    setattr(
                        pretty_module.Fore,
                        name,
                        ""
                    )


                setattr(
                    pretty_module.Style,
                    "RESET_ALL",
                    ""
                )
                
                
                print("SPI ENGINE IMPORT SUCCESS")
                `);
                
                
                
                
                appendToTerminal(
                    "[OK] SPI Engine imported successfully",
                    "success"
                );
                
                appendToTerminal(
                    "[SYS] Pyodide ready. Waiting for SPI bridge...",
                    "system"
                );

                // Update UI to Ready State
                // Update UI to Ready State

                isPyodideReady = true;


                if(statusIcon){
                
                    statusIcon.setAttribute(
                        'data-lucide',
                        'check-circle'
                    );
                
                
                    statusIcon.classList.remove(
                        'animate-spin',
                        'text-blue-400'
                    );
                
                
                    statusIcon.classList.add(
                        'text-emerald-400'
                    );
                
                }


                statusText.textContent =
                "System Ready";


                statusBadge.classList.replace(
                    'border-base-700',
                    'border-emerald-500/20'
                );


                statusBadge.classList.replace(
                    'bg-base-900',
                    'bg-emerald-500/5'
                );


                lucide.createIcons();



                appendToTerminal(
                    "[OK] System Ready. Awaiting user input.\n",
                    "success"
                );

                appendToTerminal(
                "==============================================================",
                "system"
                );
                
                appendToTerminal(
                "TPM-SCOPE",
                "success"
                );
                
                appendToTerminal(
                "TPM 2.0 SPI Transaction Reconstruction & Analysis Framework"
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Developed by Arush Mangalam Bajpai",
                "system"
                );
                
                appendToTerminal(
                "==============================================================",
                "system"
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "========================= USER GUIDE =========================",
                "success"
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Single Transaction Decode",
                "system"
                );
                
                appendToTerminal(
                "  Decode individual TPM transactions using raw MOSI"
                );
                
                appendToTerminal(
                "  or complete MOSI + MISO SPI data."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Supported Interfaces",
                "system"
                );
                
                appendToTerminal(
                "  Supports both TPM 2.0 FIFO and CRB interfaces."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "CSV Analysis Pipeline",
                "system"
                );
                
                appendToTerminal(
                "  Upload a Saleae Logic Analyzer CSV to reconstruct"
                );
                
                appendToTerminal(
                "  and analyze the complete TPM communication stream."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Step 1  - Transaction Builder"
                );
                
                appendToTerminal(
                "          Reconstructs complete SPI transactions."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Step 2  - Transaction Decoder"
                );
                
                appendToTerminal(
                "          Decodes TPM register accesses and TPM commands."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Step 3  - TPM Command Summary"
                );
                
                appendToTerminal(
                "          Summarizes all TPM commands observed."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Step 4  - PCR Extend Summary"
                );
                
                appendToTerminal(
                "          Lists PCR Extend operations and digests."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Transaction Inspector",
                "system"
                );
                
                appendToTerminal(
                "  Decode any reconstructed transaction by index."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Transaction Explorer",
                "system"
                );
                
                appendToTerminal(
                "  Browse reconstructed transactions interactively"
                );
                
                appendToTerminal(
                "  and click any entry to view its complete decode."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Downloads",
                "system"
                );
                
                appendToTerminal(
                "  Export generated CSV files and analysis reports."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "Documentation",
                "system"
                );
                
                appendToTerminal(
                "  For complete documentation and updates,"
                );
                
                appendToTerminal(
                "  visit the project GitHub repository."
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "==============================================================",
                "system"
                );
                
                appendToTerminal("");
                
                appendToTerminal(
                "[OK] Ready for analysis.",
                "success"
                );
            } catch (error) {
                appendToTerminal(`[FATAL] Failed to load engine.\n${error}`, "error");
                document.getElementById('engine-status-text').textContent = "Engine Failed";
            }
        }
        

        async function runSingleDecode() {
            if (!isPyodideReady) {
                appendToTerminal("[ERR] Engine not ready.", "error");
                return;
            }

            const interfaceType = document.querySelector('input[name="interface"]:checked').value;
            const mosi = document.getElementById('mosi-input').value.trim();
            const miso = document.getElementById('miso-input').value.trim();

            if (!mosi) {
                appendToTerminal("[ERR] MOSI input required.", "error");
                return;
            }

            appendToTerminal(`\n$ decode_spi --interface ${interfaceType} --mode ${currentMode}`, "system");
            
            try {
                pyodideInstance.globals.set("ui_mosi", mosi);
                pyodideInstance.globals.set("ui_miso", miso);
                pyodideInstance.globals.set("ui_interface", interfaceType);
                pyodideInstance.globals.set("ui_mode", currentMode);
                const result =
                await pyodideInstance.runPythonAsync(`
                
                import io
                import contextlib
                
                
                output = io.StringIO()
                with contextlib.redirect_stdout(output):

                    if ui_mode == "MOSI":

                        obj = decode_mosi(
                            ui_mosi,
                            ui_interface
                        )

                        obj.show()


                    else:

                        mosi_obj, miso_obj = decode_transaction(
                            ui_mosi,
                            ui_miso,
                            ui_interface
                        )


                        print(
                            "========== MOSI =========="
                        )
                                        
                        if mosi_obj is not None:
                                        
                            mosi_obj.show()
                                        
                        else:
                                        
                            print("No MOSI object generated.")
                                        
                        if miso_obj is not None:
                                        
                            print(
                                "\\n========== MISO =========="
                            )
                                        
                            miso_obj.show()
                                        
                        else:
                                        
                            print(
                                "\\n========== MISO =========="
                            )
                                        
                            print("No MISO object generated for this transaction.")

                
                
                output.getvalue()
                
                `);
                appendToTerminal(result);
                appendToTerminal("[OK] Decode completed successfully.\n", "success");

            } catch (error) {
                appendToTerminal(`[ERR] Exception in Python execution.\n${error}`, "error");
            }
        }

        // ==========================================
        // CSV ANALYZER LOGIC
        // ==========================================
        
        let hasUploadedCSV = false;

        async function handleFileUpload(event) {
        
            const file = event.target.files[0];
        
            if (!file) return;
        
        
            appendToTerminal(
                `[SYS] Mounting ${file.name} into Pyodide FS...`,
                "system"
            );
        
        
            // update UI
        
            document.getElementById(
                "upload-text"
            ).innerHTML =
                `<span class="text-blue-400 font-mono">${file.name}</span> mounted.`;
        
        
            const dropZone =
                document.getElementById(
                    "drop-zone"
                );
            
            
            dropZone.classList.add(
                "border-blue-500/30",
                "bg-blue-500/5"
            );
        
        
            try {
            
            
                const buffer =
                    await file.arrayBuffer();
            
            
            
                pyodideInstance.FS.writeFile(
                
                    file.name,
                
                    new Uint8Array(
                        buffer
                    )
                
                );
            
            
            
                pyodideInstance.globals.set(
                
                    "uploaded_csv",
                
                    file.name
                
                );
            
            
            
                let check =
                await pyodideInstance.runPythonAsync(`
                
        import os
                
        str(os.listdir("."))
                
                `);
                
                
                
                appendToTerminal(
                
                    "[DEBUG] Pyodide FS: " + check,
                
                    "system"
                
                );
            
            
            
                appendToTerminal(
                
                    `[OK] Mounted ${file.name} successfully.`,
                
                    "success"
                
                );
            
            
            
                hasUploadedCSV = true;
            
            
            
                document
                    .getElementById("step-1")
                    .classList
                    .remove("step-disabled");
            
            
            }
        
        
            catch(error){
            
            
                appendToTerminal(
                
                    "[ERR] Upload failed:\n" + error,
                
                    "error"
                
                );
            
            
            }
        
        }

        async function runCsvStep(stepNum, outputFileName) {
            if (!hasUploadedCSV && stepNum === 1) {
                appendToTerminal("[ERR] Please upload a logic analyzer CSV first.", "error");
                return;
            }

            const stepTitles = [
                "transaction_builder.py",
                "transaction_csv_decoder.py",
                "tpm_command_summary.py",
                "pcr_extend_summaries.py"
            ];

            appendToTerminal(`\n$ python3 ${stepTitles[stepNum - 1]}`, "system");
            
            try {
            
            
                if (stepNum === 1) {
                
                
                    let result =
                    await pyodideInstance.runPythonAsync(`
                    
                        import io
                        import contextlib

                        from transaction_builder import main


                        buffer = io.StringIO()


                        with contextlib.redirect_stdout(buffer):

                            main(uploaded_csv)


                        buffer.getvalue()
                    
                    `);
                    
                    
                    
                    appendToTerminal(
                        result
                    );
                
                
                
                    appendToTerminal(
                    
                        "[OK] Generated clean_spi_transactions.csv",
                    
                        "success"
                    
                    );
                    // Unlock Transaction Inspector

                    document
                    .getElementById(
                        "decode-index-card"
                    )
                    .classList.remove(
                        "opacity-50",
                        "pointer-events-none"
                    );

                    document
                    .getElementById(
                        "decode-index-input"
                    )
                    .disabled = false;

                    document
                    .getElementById(
                        "decode-index-btn"
                    )
                    .disabled = false;

                    document
                    .getElementById(
                        "explorer-card"
                    )
                    .classList.remove(
                        "opacity-50",
                        "pointer-events-none"
                    );

                    document
                    .getElementById(
                        "explorer-btn"
                    )
                    .disabled = false;

                    const explorerIcon =
                    document.getElementById(
                        "explorer-icon"
                    );

                    explorerIcon.classList.remove(
                        "text-gray-500",
                        "border-base-700",
                        "bg-base-800"
                    );

                    explorerIcon.classList.add(
                        "text-blue-400",
                        "border-blue-500/30",
                        "bg-blue-500/10"
                    );

                    const panel =
                    document.getElementById(
                        "decode-index-panel"
                    );

                    panel.classList.add(
                        "is-active"
                    );

                    const icon =
                    document.getElementById(
                        "decode-index-icon"
                    );

                    icon.classList.remove(
                        "text-gray-500",
                        "border-base-700",
                        "bg-base-800"
                    );

                    icon.classList.add(
                        "text-blue-400",
                        "border-blue-500/30",
                        "bg-blue-500/10"
                    );
// Unlock decoded transaction step

                    let step2 =
                    document.getElementById(
                        "step-2"
                    );


                    step2.classList.remove(
                        "step-disabled"
                    );


                    step2.classList.add(
                        "is-active"
                    );
                
                
                }
                else if (stepNum === 2) {
                
                
                    let result =
                    await pyodideInstance.runPythonAsync(`
                    
                import io
                import contextlib
                    
                from transaction_csv_decoder import main
                    
                    
                buffer = io.StringIO()
                    
                    
                with contextlib.redirect_stdout(buffer):
                    
                    main()
                    
                    
                buffer.getvalue()
                    
                    `);
                    
                    
                    
                    appendToTerminal(
                        result
                    );
                
                
                
                    appendToTerminal(
                    
                        "[OK] Generated decoded_transactions.csv",
                    
                        "success"
                    
                    );
                    // Unlock TPM command summary

                    let step3 =
                    document.getElementById(
                        "step-3"
                    );


                    step3.classList.remove(
                        "step-disabled"
                    );


                    step3.classList.add(
                        "is-active"
                    );
                
                
                }
                else if (stepNum === 3) {
                
                
                    let result =
                    await pyodideInstance.runPythonAsync(`
                    
                import io
                import contextlib
                    
                from tpm_command_summary import main
                    
                    
                buffer = io.StringIO()
                    
                    
                with contextlib.redirect_stdout(buffer):
                    
                    main()
                    
                    
                buffer.getvalue()
                    
                    `);
                    
                    
                    
                    appendToTerminal(
                        result
                    );
                
                
                
                    appendToTerminal(
                    
                        "[OK] Generated tpm_command_summary.txt",
                    
                        "success"
                    
                    );
                    displayTextFile(
                        "tpm_command_summary.txt"
                    );
                    // Unlock PCR summary

                    let step4 =
                    document.getElementById(
                        "step-4"
                    );


                    step4.classList.remove(
                        "step-disabled"
                    );


                    step4.classList.add(
                        "is-active"
                    );

                    let files =
                    await pyodideInstance.runPythonAsync(`
                    
                    import os
                    
                    str(os.listdir("."))
                    
                    `);
                    
                    
                    appendToTerminal(
                        files,
                        "system"
                    );
                
                }
                else if (stepNum === 4) {
                
                
                    let result =
                    await pyodideInstance.runPythonAsync(`
                    
                import io
                import contextlib
                    
                from pcr_extend_summaries import main
                    
                    
                buffer = io.StringIO()
                    
                    
                with contextlib.redirect_stdout(buffer):
                    
                    main()
                    
                    
                buffer.getvalue()
                    
                    `);
                    
                    
                    
                    appendToTerminal(
                        result
                    );
                
                
                
                    appendToTerminal(
                    
                        "[OK] Generated pcr_extend_summary.txt",
                    
                        "success"
                    
                    );
                    displayTextFile(
                        "pcr_extend_summary.txt"
                    );
                
                
                }

                // Enable download button

                document
                    .getElementById(
                        `btn-dl-${stepNum}`
                    )
                    .classList
                    .remove(
                        "hidden"
                    );
            
            
            }

            catch(error){
            
            
                appendToTerminal(
                
                    "[ERR] CSV processing failed:\\n" + error,
                
                    "error"
                
                );
            
            
            }
        }
        async function decodeTransactionIndex(){
        
            if(!isPyodideReady){
            
                appendToTerminal(
                    "[ERR] Engine not ready.",
                    "error"
                );
            
                return;
            }
        
            const index =
            document.getElementById(
                "decode-index-input"
            ).value.trim();
        
            if(index === ""){
            
                appendToTerminal(
                    "[ERR] Transaction index required.",
                    "error"
                );
            
                return;
            }
        
            appendToTerminal(
                `\n$ inspect_transaction --index ${index}`,
                "system"
            );
        
            pyodideInstance.globals.set(
                "ui_index",
                parseInt(index)
            );
        
            try{
            
                const tx =
                await pyodideInstance.runPythonAsync(`
                
                import csv
                import json

                result = None

                with open(
                    "clean_spi_transactions.csv",
                    newline=""
                ) as f:

                    reader = csv.DictReader(f)

                    for row in reader:

                        if int(row["Index"]) == ui_index:

                            result = json.dumps({

                                "mosi": row["MOSI"].strip(),

                                "miso": row["MISO"].strip()

                            })

                            break

                result
                
                `);

                console.log(tx);
                appendToTerminal(
                    JSON.stringify(tx),
                    "system"
                );

                if(tx === null){

                    appendToTerminal(
                        "[ERR] Transaction index not found.",
                        "error"
                    );
                
                    return;
                }
                
                const data = JSON.parse(tx);
                const mosi = data.mosi;
                const miso = data.miso;

                const mode =
                (data.miso && data.miso.length > 0)
                    ? "FULL"
                    : "MOSI";
                pyodideInstance.globals.set("ui_mosi", mosi);
                pyodideInstance.globals.set("ui_miso", miso);
                pyodideInstance.globals.set("ui_interface", "FIFO");
                pyodideInstance.globals.set("ui_mode", mode);

                const result =
                await pyodideInstance.runPythonAsync(`
                
                import io
                import contextlib
                
                
                output = io.StringIO()
                with contextlib.redirect_stdout(output):

                    if ui_mode == "MOSI":

                        obj = decode_mosi(
                            ui_mosi,
                            ui_interface
                        )

                        obj.show()


                    else:

                        mosi_obj, miso_obj = decode_transaction(
                            ui_mosi,
                            ui_miso,
                            ui_interface
                        )


                        print(
                            "========== MOSI =========="
                        )
                                        
                        if mosi_obj is not None:
                                        
                            mosi_obj.show()
                                        
                        else:
                                        
                            print("No MOSI object generated.")
                                        
                        if miso_obj is not None:
                                        
                            print(
                                "\\n========== MISO =========="
                            )
                                        
                            miso_obj.show()
                                        
                        else:
                                        
                            print(
                                "\\n========== MISO =========="
                            )
                                        
                            print("No MISO object generated for this transaction.")

                
                
                output.getvalue()
                
                `);

                appendToTerminal(result);

                appendToTerminal(
                    "[OK] Transaction inspection completed.\n",
                    "success"
                );

                pyodideInstance.globals.set(
                    "ui_mosi",
                    mosi
                );

                pyodideInstance.globals.set(
                    "ui_miso",
                    miso
                );

                pyodideInstance.globals.set(
                    "ui_interface",
                    "FIFO"
                );

                pyodideInstance.globals.set(
                    "ui_mode",
                    mode
                );
                
            
            }
        
            catch(error){
            
                appendToTerminal(
                
                    "[ERR]\\n"+error,
                
                    "error"
                
                );
            
            }
        
        }

        function downloadFile(filename){
        
        
            try {
            
            
                const data =
                    pyodideInstance.FS.readFile(
                        filename
                    );
                
                
                
                const blob =
                    new Blob(
                        [data],
                        {
                            type:
                            "application/octet-stream"
                        }
                    );
                
                
                
                const url =
                    URL.createObjectURL(
                        blob
                    );
                
                
                
                const a =
                    document.createElement(
                        "a"
                    );
                
                
                
                a.href = url;
                
                
                a.download =
                    filename;
                
                
                
                document.body.appendChild(
                    a
                );
            
            
                a.click();
            
            
            
                document.body.removeChild(
                    a
                );
            
            
                URL.revokeObjectURL(
                    url
                );
            
            
            
                appendToTerminal(
                
                    `[OK] Downloaded ${filename}`,
                
                    "success"
                
                );
            
            
            }
        
        
            catch(error){
            
            
                appendToTerminal(
                
                    `[ERR] Download failed:\n${error}`,
                
                    "error"
                
                );
            
            
            }
        
        
        }
        function displayTextFile(filename){
        
        
            try {
            
            
                const data =
                    pyodideInstance.FS.readFile(
                        filename,
                        {
                            encoding: "utf8"
                        }
                    );
                
                
                appendToTerminal(
                    "\n========== " +
                    filename +
                    " ==========\n",
                    "system"
                );
            
            
                appendToTerminal(
                    data,
                    "normal"
                );
            
            
            }
        
        
            catch(error){
            
            
                appendToTerminal(
                
                    "[ERR] Cannot display file:\n" + error,
                
                    "error"
                
                );
            
            
            }
        
        
        }

        async function loadExplorerTransactions(){

            const csv =
            await pyodideInstance.runPythonAsync(`
            
        import csv
        import json
            
        rows = []
            
        with open(
            "clean_spi_transactions.csv",
            newline=""
        ) as f:
            
            reader = csv.DictReader(f)
            
            for row in reader:
            
                rows.append({
            
                    "index": int(row["Index"]),
            
                    "length": int(row["Length"]),
            
                    "mosi": row["MOSI"],
            
                    "miso": row["MISO"]
            
                })
            
        json.dumps(rows)
            
            `);
            
            explorerTransactions =
            JSON.parse(csv);
            
        }
        function populateExplorer(){
        
            const tbody =
            document.getElementById(
                "transactions-tbody"
            );
        
            tbody.innerHTML = "";
        
            explorerTransactions.forEach(tx=>{
            
                const tr =
                document.createElement(
                    "tr"
                );
            
                tr.className =
                "row-transition hover:bg-base-700/30 cursor-pointer border-l-4 border-transparent";
                tr.onclick = async () => {
                
                    if(selectedExplorerRow){
                    
                        selectedExplorerRow.classList.remove(
                            "selected-transaction"
                        );
                    
                    }
                
                    tr.classList.add(
                        "selected-transaction"
                    );
                
                    selectedExplorerRow = tr;
                
                    await decodeExplorerTransaction(tx);
                
                };
            
                tr.innerHTML = `
            
        <td class="py-1 px-3 font-medium text-gray-500">
        ${tx.index}
        </td>
            
        <td class="py-1 px-3 text-blue-400 font-semibold">
        ${tx.length}
        </td>
            
        <td class="py-1 px-3 text-gray-300 truncate max-w-[90px]">
        ${tx.mosi.substring(0,32)}...
        </td>
            
        <td class="py-1 px-3 text-emerald-400/80 truncate max-w-[90px]">
        ${tx.miso.substring(0,32)}...
        </td>
            
        `;
            
                tbody.appendChild(
                    tr
                );
            
            });
        
            document.querySelector(
                "#transaction-explorer-modal strong"
            ).textContent =
            explorerTransactions.length;
        
        }
        async function decodeExplorerTransaction(tx){
        
            const mosi = tx.mosi;
            const miso = tx.miso;
        
            const mode =
            (miso && miso.length > 0)
                ? "FULL"
                : "MOSI";
        
            pyodideInstance.globals.set(
                "ui_mosi",
                mosi
            );
        
            pyodideInstance.globals.set(
                "ui_miso",
                miso
            );
        
            pyodideInstance.globals.set(
                "ui_interface",
                "FIFO"
            );
        
            pyodideInstance.globals.set(
                "ui_mode",
                mode
            );
        
            try{
            
                const result =
                await pyodideInstance.runPythonAsync(`
                
        import io
        import contextlib
                
        output = io.StringIO()
                
        with contextlib.redirect_stdout(output):
                
            if ui_mode == "MOSI":
                
                obj = decode_mosi(
                    ui_mosi,
                    ui_interface
                )
                
                obj.show()
                
            else:
                
                mosi_obj, miso_obj = decode_transaction(
                    ui_mosi,
                    ui_miso,
                    ui_interface
                )
                
                print("========== MOSI ==========")
                
                if mosi_obj is not None:
                
                    mosi_obj.show()
                
                else:
                
                    print("No MOSI object generated.")
                
                print("\\n========== MISO ==========")
                
                if miso_obj is not None:
                
                    miso_obj.show()
                
                else:
                
                    print("No MISO object generated.")
                
        output.getvalue()
                
                `);
                
                document.getElementById(
                    "decoded-viewer"
                ).textContent =
                result;
            
            }
        
            catch(error){
            
                document.getElementById(
                    "decoded-viewer"
                ).textContent =
                error;
            
            }
        
        }

        async function openTransactionExplorer(){

            if(
                explorerTransactions.length === 0
            ){
            
                await loadExplorerTransactions();
            
            }
        
            populateExplorer();
        
            document
                .getElementById(
                    "transaction-explorer-modal"
                )
                .classList.remove(
                    "hidden"
                );
            
        }
        function closeTransactionExplorer(){

            document
                .getElementById(
                    "transaction-explorer-modal"
                )
                .classList.add(
                    "hidden"
                );
            
        }
        window.addEventListener('load', initPyodideEngine);
        
