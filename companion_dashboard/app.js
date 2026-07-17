// app.js

// Mock device dataset for the fleet
const devices = [
    {
        id: "dev-1",
        name: "Father's Workstation",
        os: "WINDOWS_11",
        state: "secure", // secure, locked, alert
        ip: "184.22.109.4",
        mac: "4A:90:D9:E3:A2:11",
        lat: 40.7128,
        lon: -74.0060,
        city: "New York, NY",
        isp: "Verizon Cloud Services",
        lastPing: "12ms",
        lastUpdate: "Just Now"
    },
    {
        id: "dev-2",
        name: "Mother's Laptop",
        os: "WINDOWS_10",
        state: "secure",
        ip: "82.165.12.89",
        mac: "BC:2E:8F:A1:04:99",
        lat: 51.5074,
        lon: -0.1278,
        city: "London, UK",
        isp: "British Telecom Cloud",
        lastPing: "28ms",
        lastUpdate: "3 mins ago"
    },
    {
        id: "dev-3",
        name: "Office Domain Controller",
        os: "WIN_SERVER_2022",
        state: "locked",
        ip: "46.165.2.14",
        mac: "00:1A:2B:3C:4D:5E",
        lat: 50.1109,
        lon: 8.6821,
        city: "Frankfurt, DE",
        isp: "Deutsche Telekom AG",
        lastPing: "35ms",
        lastUpdate: "12 mins ago"
    },
    {
        id: "dev-4",
        name: "Sister's Gaming PC",
        os: "WINDOWS_11",
        state: "alert",
        ip: "122.211.45.109",
        mac: " Tokyo, JP",
        lat: 35.6762,
        lon: 139.6503,
        city: "Tokyo, JP",
        isp: "SoftBank Corp.",
        lastPing: "85ms",
        lastUpdate: "1 min ago"
    }
];

let selectedDeviceId = "dev-1";

// DOM Elements
const devicesGrid = document.getElementById("devices-grid");
const selectedDeviceTitle = document.getElementById("selected-device-title");
const selectedDeviceTag = document.getElementById("selected-device-tag");
const statePulsar = document.getElementById("state-pulsar");
const stateValue = document.getElementById("state-value");
const mapCoordinates = document.getElementById("map-coordinates");
const mapCityLabel = document.getElementById("map-city-label");
const terminalBody = document.getElementById("terminal-body");
const feedContainer = document.getElementById("feed-container");
const activeDevicesCount = document.getElementById("active-devices-count");

// Render all device cards in the grid
function renderDeviceCards() {
    devicesGrid.innerHTML = "";
    devices.forEach(dev => {
        const card = document.createElement("div");
        card.className = `device-card ${dev.id === selectedDeviceId ? 'selected' : ''}`;
        card.onclick = () => selectDevice(dev.id);

        card.innerHTML = `
            <div class="device-card-header">
                <h4>${dev.name}</h4>
                <span class="os-icon">${dev.os}</span>
            </div>
            <div class="device-card-status">
                <span class="status-dot ${dev.state}"></span>
                <span style="text-transform: capitalize; font-weight: 600;">${dev.state}</span>
            </div>
            <div class="device-card-meta">
                <span>IP: ${dev.ip}</span>
                <span>Last Activity: ${dev.lastUpdate}</span>
            </div>
        `;
        devicesGrid.appendChild(card);
    });
    
    // Count active devices
    activeDevicesCount.innerText = devices.length;
}

// Select active device to display details
function selectDevice(deviceId) {
    selectedDeviceId = deviceId;
    renderDeviceCards();
    
    const dev = devices.find(d => d.id === deviceId);
    if (!dev) return;

    // Update Details panel
    selectedDeviceTitle.innerText = dev.name;
    selectedDeviceTag.innerText = dev.os;
    
    // Update State Indicators
    statePulsar.className = `state-pulsar ${dev.state}`;
    stateValue.className = `state-value ${dev.state}`;
    stateValue.innerText = dev.state.toUpperCase();

    // Update Coordinates & Map mock labels
    mapCoordinates.innerText = `Lat: ${dev.lat.toFixed(4)}, Lon: ${dev.lon.toFixed(4)}`;
    mapCityLabel.innerText = `${dev.city} (ISP: ${dev.isp})`;

    // Simulate location radar adjustment animation
    const sweep = document.querySelector(".radar-sweep");
    sweep.style.animation = "none";
    void sweep.offsetWidth; // trigger reflow
    sweep.style.animation = "sweep 4s linear infinite";

    // Write select message to terminal
    writeToTerminal(`[SYSTEM] Switched console focus to target device: ${dev.name} [IP: ${dev.ip}]`);
}

// Write line of text to terminal
function writeToTerminal(text) {
    terminalBody.innerHTML += "\n" + text;
    terminalBody.scrollTop = terminalBody.scrollHeight;
}

// Clear terminal logs
function clearTerminal() {
    terminalBody.innerHTML = "[SYSTEM] Console logs cleared. Ready for next command.";
}

// Simulate command execution via Websocket / API
function sendCommand(cmd) {
    const dev = devices.find(d => d.id === selectedDeviceId);
    if (!dev) return;

    // HMAC Gated Authorization Header simulation
    writeToTerminal(`\n> Dispatching ${cmd} --token=HMAC_SHA256_AUTH_VALID...`);
    writeToTerminal(`[WEBSOCKET] Sending command payload to gateway...`);

    setTimeout(() => {
        if (cmd === "/ping") {
            writeToTerminal(`[RESPONSE] PONG received from client!`);
            writeToTerminal(`[RESPONSE] Host: ${dev.name} | RTT Latency: ${dev.lastPing} | State: ${dev.state.toUpperCase()}`);
            addFeedEvent(dev.name, `Responded to remote /ping command [RTT: ${dev.lastPing}].`, dev.state);
        } 
        else if (cmd === "/lock") {
            writeToTerminal(`[RESPONSE] Authorization: OK (Integrity level: Medium)`);
            writeToTerminal(`[RESPONSE] Locking workstation screen session...`);
            setTimeout(() => {
                dev.state = "locked";
                selectDevice(selectedDeviceId);
                writeToTerminal(`[RESPONSE] ✅ Workstation lock command succeeded.`);
                addFeedEvent(dev.name, "Workstation locked remotely via administration dashboard.", "locked");
            }, 1000);
        }
        else if (cmd === "/unlock") {
            if (dev.state === "secure") {
                writeToTerminal(`[RESPONSE] Device vault is already unlocked.`);
                return;
            }
            writeToTerminal(`[RESPONSE] Instantiating VaultModule decryption routine...`);
            writeToTerminal(`[RESPONSE] Gating symmetric Fernet key decryption via DPAPI...`);
            setTimeout(() => {
                dev.state = "secure";
                selectDevice(selectedDeviceId);
                writeToTerminal(`[RESPONSE] ✅ In-place files decrypted successfully. Vault status: UNLOCKED.`);
                addFeedEvent(dev.name, "Workstation vault unlocked and decrypted successfully.", "secure");
            }, 1200);
        }
        else if (cmd === "/report") {
            writeToTerminal(`[RESPONSE] Gathering active forensic metadata...`);
            writeToTerminal(`[RESPONSE] Constructing timeline logs & embedding intruder capture...`);
            setTimeout(() => {
                writeToTerminal(`[RESPONSE] Compiling security PDF report via ReportLab...`);
                setTimeout(() => {
                    writeToTerminal(`[RESPONSE] PDF compiled: VigiLo_Incident_Report_2026.pdf (Size: 142KB)`);
                    writeToTerminal(`[RESPONSE] 📤 Uploading document to active Telegram/WhatsApp alert channels...`);
                    writeToTerminal(`[RESPONSE] ✅ Upload completed. Document sent successfully.`);
                    addFeedEvent(dev.name, "Forensic security report generated and sent to alert channels.", dev.state);
                }, 1000);
            }, 800);
        }
        else if (cmd === "/locate") {
            writeToTerminal(`[RESPONSE] Scanning wireless spectrum triangulation networks...`);
            setTimeout(() => {
                writeToTerminal(`[RESPONSE] Triangulation match: Lat ${dev.lat.toFixed(6)} | Lon ${dev.lon.toFixed(6)}`);
                writeToTerminal(`[RESPONSE] Location resolved: ${dev.city} (via ISP: ${dev.isp})`);
                addFeedEvent(dev.name, `Location scanned and geolocated: ${dev.city}.`, dev.state);
            }, 1500);
        }
    }, 800);
}

// Add an event to the sidebar live security feed
function addFeedEvent(deviceName, message, state) {
    const item = document.createElement("div");
    item.className = `feed-item ${state}`;
    
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];

    item.innerHTML = `
        <div class="feed-item-header">
            <strong>${deviceName}</strong>
            <span>${timeStr}</span>
        </div>
        <div class="feed-item-body">${message}</div>
    `;

    feedContainer.insertBefore(item, feedContainer.firstChild);
    
    // Keep only the last 15 feed items
    if (feedContainer.children.length > 15) {
        feedContainer.removeChild(feedContainer.lastChild);
    }
}

// Simulate periodic WebSocket incoming events
function simulateLiveFeed() {
    const messages = [
        { deviceIndex: 0, text: "Failed logon attempt: invalid password hash.", state: "locked" },
        { deviceIndex: 1, text: "IP address changed: lease renewed on DHCP.", state: "secure" },
        { deviceIndex: 2, text: "System stats compiled: CPU 12% | RAM 45%.", state: "secure" },
        { deviceIndex: 3, text: "Owner detected: Face verification match. Suppression active.", state: "secure" },
        { deviceIndex: 3, text: "⚠️ Intruder detected! Wrong password threshold. Lock vault active.", state: "alert" },
        { deviceIndex: 0, text: "Workstation status heartbeat received (Medium Integrity).", state: "secure" }
    ];

    setInterval(() => {
        const randIndex = Math.floor(Math.random() * messages.length);
        const msg = messages[randIndex];
        const dev = devices[msg.deviceIndex];
        
        // If it's a critical alert, we transition state
        if (msg.state === "alert") {
            dev.state = "alert";
            renderDeviceCards();
            if (selectedDeviceId === dev.id) {
                selectDevice(dev.id);
            }
        }

        addFeedEvent(dev.name, msg.text, msg.state);
    }, 15000); // every 15 seconds
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    renderDeviceCards();
    selectDevice("dev-1");
    
    // Add initial feed events
    addFeedEvent("Office Domain Controller", "VigiLo service initialized in SYSTEM context.", "secure");
    addFeedEvent("Father's Workstation", "Owner enrolled face profile loaded successfully.", "secure");
    addFeedEvent("Sister's Gaming PC", "⚠️ Intruder detected: Camera alert dispatched to Telegram.", "alert");
    
    simulateLiveFeed();
});
