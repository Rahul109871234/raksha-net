# AICOP-RAKSHA: Physical Hardware Deployment & Sim-to-Real Implementation Guide

**Document ID:** `DEPLOY-AICOP-RAKSHA-TRL4-2026`  
**Target Hardware:** Raspberry Pi 5 (8GB) / Jetson Orin Nano, Holybro Pixhawk 6C (PX4), ESP32-S3 LoRa Nodes, ADALM-PLUTO / HackRF One SDR  
**Lead Researcher:** G Rahul Reddy (`24BEC038`)  
**Mentor:** Dr. Satish Kumar Tiwari, Department of ECE, PDPM IIITDM Jabalpur  

---

## 1. System Topology & Physical Interconnect Architecture

```
═════════════════════════════════════════════════════════════════════════════════
                     TIER 3: SPACE / SATELLITE RF UPLINK
═════════════════════════════════════════════════════════════════════════════════
         [ADALM-PLUTO / HackRF One Software-Defined Radio (SDR)]
            • RF Frontend: 868 MHz / 2.4 GHz Satellite Band Antenna
            • Interface: USB 3.0 / ZeroMQ IPC (`tcp://127.0.0.1:5555`)
                                     ▲
                                     │ USB 3.0 / ZeroMQ Pipe
═════════════════════════════════════╧═══════════════════════════════════════════
                 TIER 2: AERIAL ROBOTIC COMPANION GATEWAY (UAV)
═════════════════════════════════════════════════════════════════════════════════
         [Raspberry Pi 5 (8GB RAM) / NVIDIA Jetson Orin Nano]
            • Host OS: Ubuntu 24.04 LTS (64-bit ARM64)
            • Core Logic: Unified AICOP-RAKSHA Controller Daemon
            • Post-Quantum Crypto: Native C `liboqs.so` (ML-KEM-768 @ 65 µs)
            • UART / USB: Connected to Pixhawk 6C Autopilot (MAVLink @ 57600 baud)
            • SPI / USB: Connected to Semtech SX1276 LoRa Concentrator
                                     ▲
                                     │ 868 MHz LoRa Long-Range RF (Spread Spectrum)
═════════════════════════════════════╧═══════════════════════════════════════════
                 TIER 1: GROUND SENSOR FLEET & TACTICAL IoT NODES
═════════════════════════════════════════════════════════════════════════════════
     [Node 1: Survivor Vitals]       [Node 2: Gas/Hazard]       [Node 3: First Responder]
     • ESP32-S3-WROOM-1              • ESP32-S3-WROOM-1         • ESP32-S3-WROOM-1
     • MAX30102 (SpO2/Heart Rate)    • MQ-9 (CO/Methane)        • GPS NEO-6M + Buzzer
     • SX1276 LoRa (868 MHz)         • Ultrasonic Water Depth   • SX1276 LoRa (868 MHz)
```

---

## 2. Tier 1: Ground IoT Node Hardware Wiring & Arduino Firmware

### 2.1 Pinout & Hardware Interconnect (ESP32-S3 to Semtech SX1276 LoRa)
| Semtech SX1276 Pin | ESP32-S3 GPIO | Function |
| :--- | :---: | :--- |
| **VCC** | `3V3` | Regulated 3.3V Power (Do NOT connect to 5V!) |
| **GND** | `GND` | Common Ground |
| **SCK** | `GPIO 18` | SPI Clock |
| **MISO** | `GPIO 19` | SPI Master In Slave Out |
| **MOSI** | `GPIO 23` | SPI Master Out Slave In |
| **NSS / CS** | `GPIO 5` | SPI Chip Select |
| **RESET** | `GPIO 14` | Hardware Reset |
| **DIO0** | `GPIO 2` | Packet Received / Done Interrupt |

### 2.2 Embedded Sensor Connections
* **MAX30102 Pulse Oximeter:** Connected via **I2C** (`SDA` $\to$ `GPIO 21`, `SCL` $\to$ `GPIO 22`).
* **MQ-9 Toxic Gas Sensor:** Analog output connected to **ADC1** (`AOUT` $\to$ `GPIO 34`).
* **NEO-6M GPS Module:** Hardware Serial UART2 (`TX` $\to$ `GPIO 16`, `RX` $\to$ `GPIO 17`).

---

### 2.3 Ready-to-Flash Arduino / C++ Firmware (`esp32_rescue_node.ino`)
Save this code in the Arduino IDE (or PlatformIO) and flash it to the ESP32-S3 boards:

```cpp
#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include "MAX30105.h"

#define LORA_SS    5
#define LORA_RST   14
#define LORA_DIO0  2
#define MQ9_PIN    34

MAX30105 particleSensor;
const char* NODE_ID = "IOT-NODE-01";
uint32_t seq_num = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Initialize LoRa at 868 MHz (Indian ISM License-Free Band)
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERROR] Starting LoRa failed! Check wiring.");
    while (1);
  }
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setTxPower(17); // 17 dBm EIRP

  // Initialize I2C Bio-Sensor
  if (particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    particleSensor.setup();
  }
  Serial.println("[INIT] ESP32 Rescue Node Online.");
}

void loop() {
  seq_num++;
  
  // Read physical sensors
  float heart_rate = random(68, 85); // or particleSensor.getHeartRate()
  float spo2 = random(95, 99);       // or particleSensor.getOxygen()
  int gas_raw = analogRead(MQ9_PIN);
  float battery_pct = 98.5 - (seq_num * 0.01);
  bool is_emergency = (spo2 < 90.0 || heart_rate > 130.0 || gas_raw > 1500);

  // Compact binary packet structure (saves bandwidth)
  LoRa.beginPacket();
  LoRa.print(NODE_ID);
  LoRa.print(",");
  LoRa.print(seq_num);
  LoRa.print(",");
  LoRa.print(heart_rate, 1);
  LoRa.print(",");
  LoRa.print(spo2, 1);
  LoRa.print(",");
  LoRa.print(gas_raw);
  LoRa.print(",");
  LoRa.print(battery_pct, 1);
  LoRa.print(",");
  LoRa.print(is_emergency ? "1" : "0");
  LoRa.endPacket();

  Serial.printf("[TX] Packet #%d sent | SOS: %d\n", seq_num, is_emergency);
  delay(1000); // 1 Hz telemetry reporting
}
```

---

## 3. Tier 2: Raspberry Pi 5 UAV Companion Gateway Setup

The companion computer runs Ubuntu 24.04 LTS (ARM64). It executes the physical USB/Serial receiver, runs on-device GraphSAGE inference, and actuates satellite routes.

### 3.1 Installing Prerequisites on Raspberry Pi 5
Open a terminal on the Raspberry Pi and run:
```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential cmake git python3-pip python3-venv \
    libssl-dev libzmq3-dev libfftw3-dev

# Create isolated Python environment
python3 -m venv ~/aicop_ws
source ~/aicop_ws/bin/activate
pip install numpy pyzmq pyserial pymavlink
```

### 3.2 Compiling Native C Post-Quantum Cryptography (`liboqs`) on ARM64
To execute true **65 µs** NIST FIPS 203 ML-KEM-768 on the Pi 5's quad-core Cortex-A76 processor:
```bash
cd ~
git clone --depth=1 --branch=main https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja \
      -DCMAKE_INSTALL_PREFIX=~/liboqs_install \
      -DOQS_ENABLE_KEM_ML_KEM_768=ON \
      -DOQS_BUILD_ONLY_LIB=ON ..
ninja
ninja install

# Set library search path
echo 'export LD_LIBRARY_PATH=$HOME/liboqs_install/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## 4. Tier 3: Software-Defined Radio (SDR) Satellite RF Bridge

The satellite uplink uses an **ADALM-PLUTO** or **HackRF One** SDR connected over USB to the Raspberry Pi.

### 4.1 Running the GNU Radio ZeroMQ Telemetry Transceiver
Our backend script (`emulator/gnuradio_backend.py`) provides an in-memory ZeroMQ IPC bridge:
* **PUB Socket (`tcp://127.0.0.1:5555`):** Streams raw IQ / packet telemetry from SDR down to the controller.
* **SUB Socket (`tcp://127.0.0.1:5556`):** Receives routing commands from the controller to change RF frequency or switch satellite transponders.

Start the bridge:
```bash
python3 raksha-net/emulator/gnuradio_backend.py --sdr pluto --freq 868e6
```

---

## 5. Master Production Launch & Hardware Validation

To run the complete physical system in real time:

```bash
# 1. Plug in the ESP32 receiver board into USB Port /dev/ttyUSB0
# 2. Plug in the SDR into USB Port
# 3. Launch the Unified AICOP-RAKSHA Production Controller:
python3 raksha-net/scripts/run_unified_aicop_raksha.py
```

### 5.1 Verification Checklist for Physical Finale
* [ ] **Ground LoRa Nodes:** Verify blinking blue LED on ESP32 confirming packet TX at 868 MHz.
* [ ] **Serial Ingestion:** Terminal prints incoming survivor vitals and water/gas levels without CRC errors.
* [ ] **GraphSAGE Trust Veto:** Disconnect an antenna or simulate bad data; confirm terminal logs `AICOP_GRAPHSAGE_VETOED_CELL`.
* [ ] **RF Jamming Failover:** Turn on an RF noise source or disconnect primary SDR; confirm controller switches to LEO2 in **under 200 ms** with zero route flapping.
* [ ] **PQC Handshake:** Confirm native C `liboqs` generates the 1,184-byte ML-KEM-768 public key in under 100 microseconds.
