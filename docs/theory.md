# Documentation

## Table of Contents
3. [USRP](#usrp)
    - [What is USRP ?](#what-is-usrp-?)
    - [](#data-sources)


---
## USRP
sdffsags
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

