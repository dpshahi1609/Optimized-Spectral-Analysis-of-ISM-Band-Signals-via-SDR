# Documentation

## Table of Contents
1. [USRP](#usrp)
    - [What is USRP ?](#what-is-usrp-?)
    - [USRP B210 Technical Specifications](#usrp-b210-technical-specifications)
    - [](#)


---
## USRP

### What is USRP ?

**USRP** stands for **Universal Software Radio Peripheral**. It is a flexible and widely used family of **Software-Defined Radio (SDR)** hardware platforms designed and originally developed by **Ettus Research** (now a brand of **National Instruments**).

In simple terms, a USRP connects a standard computer to the radio frequency (RF) spectrum. It acts as a bridge that allows software on your computer to process live radio signals (receive) or generate new radio signals (transmit).

#### Core Architecture
A typical USRP device consists of two main hardware sections that work together:

1.  **Motherboard (Digital Processing):**
    * Contains **High-speed ADCs and DACs** (Analog-to-Digital and Digital-to-Analog Converters) to translate signals between the real world and the digital domain.
    * Includes an **FPGA** (Field Programmable Gate Array) for high-speed digital tasks like down-conversion and decimation.
    * Provides the interface to the host computer (via USB, Gigabit Ethernet, or PCIe).

2.  **Daughterboard (RF Front End):**
    * A modular circuit board that handles the analog radio signals.
    * Performs signal conditioning, such as amplification, filtering, and up/down-conversion to the specific frequency bands you need (e.g., FM radio, Wi-Fi, Cellular).

#### Software Ecosystem
The USRP hardware is useless without software. It is primarily controlled by the **UHD (USRP Hardware Driver)**, which provides the necessary drivers and APIs. Common software frameworks used with USRP include:
* **GNU Radio:** An open-source toolkit for building signal processing graphs.
* **MATLAB / Simulink:** For algorithm design and simulation.
* **LabVIEW:** For graphical system design (common with NI hardware).
* **C++ / Python:** For custom direct programming using the UHD API.

#### Common Applications
* **Wireless Research:** Prototyping next-generation networks (5G/6G).
* **Spectrum Monitoring:** analyzing radio traffic and interference.
* **Cybersecurity:** Researching wireless vulnerabilities.
* **Public Safety:** Creating custom communication systems.

#### References
* [Ettus Research - About USRP](https://www.ettus.com/about/)
* [Digilent - What is USRP? A Beginner-to-Expert Guide](https://digilent.com/blog/what-is-usrp-a-beginner-to-expert-guide-to-software-defined-radio/)
* [National Instruments (NI) - What is a USRP Device?](https://www.ni.com/en/shop/wireless-design-test/what-is-a-usrp-software-defined-radio.html)


### USRP B210 Technical Specifications

The **USRP B210** is a fully integrated, single-board, Universal Software Radio Peripheral designed for low-cost experimentation and system prototyping. It features a wide frequency range and high bandwidth capabilities, powered by the Analog Devices AD9361 RFIC and a Xilinx Spartan-6 FPGA.

#### Hardware Architecture

| Component | Specification |
| :--- | :--- |
| **RF Transceiver Chip** | Analog Devices AD9361 |
| **FPGA** | Xilinx Spartan-6 XC6SLX150 |
| **Host Interface** | USB 3.0 SuperSpeed (Connector: Standard-B) |
| **Form Factor** | 97 x 155 x 15 mm |
| **Weight** | 350 g |

#### RF Specifications

| Feature | Details |
| :--- | :--- |
| **Frequency Range** | 70 MHz – 6 GHz |
| **Maximum Bandwidth** | 56 MHz (real-time) |
| **Channel Count** | 2 TX / 2 RX (Full Duplex) |
| **MIMO Capability** | 2x2 MIMO (Coherent) |
| **Maximum Output Power** | > 10 dBm |
| **Receive Noise Figure** | < 8 dB |
| **IIP3 (at typical NF)** | -20 dBm |
| **SSB/LO Suppression** | -35/50 dBc |

#### Conversion Performance (ADC/DAC)

| Feature | Details |
| :--- | :--- |
| **ADC Sample Rate (Max)** | 61.44 MS/s |
| **ADC Resolution** | 12 bits |
| **DAC Sample Rate (Max)** | 61.44 MS/s |
| **DAC Resolution** | 12 bits |
| **Wideband SFDR** | 78 dBc |

#### Clocking and Synchronization

| Feature | Details |
| :--- | :--- |
| **Frequency Accuracy** | ±2.0 ppm (Standard TCXO) |
| **With GPSDO (Unlocked)** | ±75 ppb |
| **With GPSDO (Locked)** | < 1 ppb |
| **External Reference** | 10 MHz Reference Input |
| **Time Reference** | PPS (Pulse Per Second) Input |

#### Power Requirements

* **Input Voltage:** 6V DC
* **Power Source:** External DC power supply (included) or USB bus power (limited capabilities depending on host).

#### Throughput Capabilities

* **1x1 SISO:** Up to 56 MHz of instantaneous bandwidth.
* **2x2 MIMO:** Up to 30.72 MHz of instantaneous bandwidth.

---
#### Sources
* [Ettus Research - USRP B200/B210 Datasheet](https://www.ettus.com/wp-content/uploads/2019/01/b200-b210_spec_sheet.pdf)
* [Digilent - NI Ettus USRP B210 Product Page](https://digilent.com/shop/ni-ettus-usrp-b210-2x2-70mhz-6ghz-sdr-cognitive-radio/)
* [Ettus Knowledge Base - B200/B210 Features](https://kb.ettus.com/B200/B210/B200mini/B205mini)
