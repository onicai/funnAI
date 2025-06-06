<script lang="ts">
    import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';
    import { onDestroy, onMount } from 'svelte';
    import Modal from './CommonModal.svelte';
    //import { toastStore } from "$lib/stores/toastStore";
    import { Principal } from "@dfinity/principal";

    // Props
    export let isOpen: boolean = false;
    export let onClose: () => void = () => {};
    export let onScan: (text: string) => void = () => {};


    // State variables
    let scanner: Html5Qrcode | null = null;
    let scannedData: string | null = null;
    let showConfirmation: boolean = false;
    let modalMounted: boolean = false;
    let fileInput: HTMLInputElement;


    async function checkCameraSupport() {
        try {
            const devices = await Html5Qrcode.getCameras();
            return devices.length > 0;
        } catch (err) {
            console.error('Error checking cameras:', err);
            return false;
        }
    }

    async function startScanner() {
        if (!scanner) return;
        
        try {
            if (scanner.isScanning) {
                await scanner.stop();
            }

            const devices = await Html5Qrcode.getCameras();
            if (!devices?.length) throw new Error('No cameras found');

            // Prefer back camera
            const selectedCamera = devices.find(device => 
                device.label.toLowerCase().includes('back') || 
                device.label.toLowerCase().includes('rear')
            ) || devices[0];

            const config = {
                fps: 10,
                qrbox: { width: 250, height: 250 },
                videoConstraints: {
                    deviceId: selectedCamera.id,
                    width: { min: 640, ideal: 1080, max: 1920 },
                    height: { min: 480, ideal: 720, max: 1080 }
                }
            };

            await scanner.start(
                selectedCamera.id,
                config,
                async (decodedText: string) => {
                    if (scanner) await scanner.stop();
                    scannedData = decodedText.trim();
                    showConfirmation = true;
                },
                () => {} // Suppress error messages during scanning
            );
        } catch (err) {
            console.error('Error starting scanner:', err);
            //toastStore.error('Failed to start camera. Please check permissions and ensure you\'re using HTTPS.');
            onClose();
        }
    }

    async function initializeScanner() {
        try {
            if (scanner?.isScanning) {
                await scanner.stop();
                scanner.clear();
            }
            scanner = null;

            scanner = new Html5Qrcode("qr-reader", { 
                verbose: false,
                formatsToSupport: [ Html5QrcodeSupportedFormats.QR_CODE ]
            });
            
            const hasCamera = await checkCameraSupport();
            if (hasCamera) {
                await startScanner();
            } else {
                //toastStore.info('No camera available. You can still upload QR code images.');
            }
        } catch (err) {
            console.error('Error initializing scanner:', err);
            //toastStore.error('Camera not available. You can still upload QR code images.');
        }
    }

    async function closeScanner() {
        if (scanner?.isScanning) {
            try {
                await scanner.stop();
                scanner.clear();
            } catch (err) {
                console.error('Error closing scanner:', err);
            }
        }
        scanner = null;
        scannedData = null;
        showConfirmation = false;
        onClose();
    }

    async function handleFileUpload(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files?.length) return;

        try {
            if (!scanner) {
                scanner = new Html5Qrcode("qr-reader");
            }
            const result = await scanner.scanFile(input.files[0], true) as string;
            scannedData = result.trim();
            showConfirmation = true;
        } catch (err) {
            console.error('Error scanning file:', err);
            //toastStore.error('Failed to scan QR code from image');
        }
    }

    function handleConfirmScan() {
        if (scannedData) {
            onScan(scannedData);
            closeScanner();
        }
    }

    function handleRejectScan() {
        scannedData = null;
        showConfirmation = false;
        startScanner();
    }

    function getAddressType(address: string): 'principal' | 'account' | 'unknown' {
        // Check for Account ID (64 character hex string)
        if (address.length === 64 && /^[0-9a-fA-F]+$/.test(address)) {
            return 'account';
        }

        // Check for Principal ID
        try {
            Principal.fromText(address);
            return 'principal';
        } catch {
            return 'unknown';
        }
    }

    function formatAddress(address: string): string {
        if (!address) return '';
        const type = getAddressType(address);
        
        if (type === 'principal') {
            // For Principal IDs, show more context: xxxx-xxxx...xxxx-xxxx
            const segments = address.split('-');
            if (segments.length > 4) {
                return `${segments.slice(0, 2).join('-')}...${segments.slice(-2).join('-')}`;
            }
        } else if (type === 'account') {
            // For Account IDs, show first and last 10 chars
            const start = address.slice(0, 10);
            const end = address.slice(-10);
            return `${start}...${end}`;
        }
        
        return address;
    }

    onMount(() => {
        if (isOpen) {
            setTimeout(() => modalMounted = true, 100);
        }
    });

    onDestroy(() => {
        closeScanner();
    });

    // Reactive statements
    $: {
        if (isOpen) {
            setTimeout(() => modalMounted = true, 100);
        } else {
            modalMounted = false;
        }
    }

    $: if (isOpen && modalMounted) {
        initializeScanner();
    }

</script>

{#if isOpen}
<Modal
    {isOpen}
    onClose={closeScanner}
    title="Scan QR Code"
    width="min(450px, 95vw)"
    height="auto"
    className="qr-scanner-modal"
>
    <div class="scanner-container">
        {#if showConfirmation}
            <div class="confirmation-dialog">
                <h3>Confirm Scanned Address</h3>
                <div class="scanned-data">
                    <div class="address-type">
                        {#if getAddressType(scannedData || '') === 'principal'}
                            <span class="badge principal">
                                <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                    <circle cx="12" cy="7" r="4" />
                                </svg>
                                Principal ID
                            </span>
                        {:else if getAddressType(scannedData || '') === 'account'}
                            <span class="badge account">
                                <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="2" y="4" width="20" height="16" rx="2" />
                                    <path d="M12 12h.01" />
                                </svg>
                                Account ID
                            </span>
                        {:else}
                            <span class="badge unknown">
                                <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10" />
                                    <path d="M12 16v-4M12 8h.01" />
                                </svg>
                                Unknown Format
                            </span>
                        {/if}
                    </div>
                    <div class="address-display">
                        <div class="formatted-address">
                            {formatAddress(scannedData || '')}
                        </div>
                        <div class="divider" />
                        <div class="full-address-container">
                            <span class="label">Full Address</span>
                            <span class="full-address">{scannedData}</span>
                        </div>
                    </div>
                </div>
                <div class="confirmation-buttons">
                    <button 
                        class="confirm-btn"
                        on:click={handleConfirmScan}
                        disabled={getAddressType(scannedData || '') === 'unknown'}
                    >
                        Confirm
                    </button>
                    <button 
                        class="reject-btn"
                        on:click={handleRejectScan}
                    >
                        Scan Again
                    </button>
                </div>
            </div>
        {:else}
            <div id="qr-reader" style="width: 100%; max-width: 300px;"></div>
            <div class="scanner-controls">
                <div class="primary-controls">
                    <button 
                        class="cancel-scan-btn"
                        on:click={closeScanner}
                    >
                        Cancel Scan
                    </button>
                </div>
                <div class="file-upload">
                    <label class="file-upload-btn" for="qr-input">
                        Upload QR Image
                    </label>
                    <input
                        bind:this={fileInput}
                        id="qr-input"
                        type="file"
                        accept="image/*"
                        on:change={handleFileUpload}
                        class="hidden"
                    />
                </div>
            </div>
        {/if}
    </div>
</Modal>
{/if}

<style>
.scanner-container {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  min-height: 400px;
}

.hidden {
  display: none;
}

:global(#qr-reader) {
  width: 100%;
  max-width: 300px;
  margin-left: auto;
  margin-right: auto;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  overflow: hidden;
  min-height: 300px;
  position: relative;
}

:global(#qr-reader video) {
  border-radius: 0.5rem;
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
}

:global(#qr-reader__header_message),
:global(#qr-reader__filescan_input),
:global(#qr-reader__dashboard_section_csr),
:global(#qr-reader__status_span),
:global(button.html5-qrcode-element) {
  display: none;
}

:global(#qr-reader__scan_region) {
  background-color: transparent;
  border-radius: 0.5rem;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  border: 2px solid #6366f1; /* indigo-500 */
}

.scanner-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
  width: 100%;
  max-width: 300px;
}

.primary-controls {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.file-upload {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
}

.file-upload-btn {
  padding: 0.5rem 1rem;
  background-color: rgba(99, 102, 241, 0.8); /* indigo-600/80 */
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.file-upload-btn:hover {
  background-color: #6366f1; /* indigo-600 */
}

.switch-camera-btn {
  padding: 0.5rem 1rem;
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-scan-btn {
  padding: 0.5rem 1rem;
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 0.5rem;
}

.confirmation-dialog {
  width: 100%;
  max-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.confirmation-dialog h3 {
  font-size: 1.25rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.scanned-data {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.address-type {
  display: flex;
  justify-content: center;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  width: 1rem;
  height: 1rem;
}

.badge.principal {
  background-color: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.badge.account {
  background-color: rgba(34, 197, 94, 0.2);
  color: #bbf7d0;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge.unknown {
  background-color: rgba(239, 68, 68, 0.2);
  color: #fecaca;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.address-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.formatted-address {
  font-family: monospace;
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  letter-spacing: 0.05em;
}

.divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  width: 100%;
}

.full-address-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
}

.full-address {
  font-family: monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  word-break: break-word;
  text-align: center;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.confirmation-buttons {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.confirmation-buttons button {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
  font-weight: 500;
}

.confirm-btn {
  background-color: #4f46e5; /* indigo-600 */
  color: white;
}

.confirm-btn:hover {
  background-color: #4338ca; /* indigo-500 */
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reject-btn {
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.reject-btn:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

:global(.qr-scanner-modal) {
    position: relative;
    z-index: 100001; /* Ensure QR scanner is above other modals */
}

#qr-reader {
    position: relative;
    z-index: 100002; /* Ensure reader is above other elements */
}
</style>
  