# Documentation

## Table of Contents
1. [USRP](#usrp)
    - [What is USRP](#what-is-usrp)
    - [USRP B210 Technical Specifications](#usrp-b210-technical-specifications)
    - [USRP B210 Ubuntu Installation Guide UHD API](#usrp-b210-ubuntu-installation-guide-uhd-api)
    - [USRP Signal Processing Theoretical and Mathematical Explanation](#usrp-signal-processing-theoretical-and-mathematical-explanation)
    - [](#)
    - [](#)


---
## USRP
sssdsg

### What is USRP

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


### USRP B210 Ubuntu Installation Guide UHD API

This guide details the installation of the **Universal Hardware Driver (UHD)** for the **USRP B210** on Ubuntu Linux. The UHD provides the host driver and API (C++/Python) required to communicate with Ettus Research SDR devices.

#### System Prerequisites

| Component | Requirement |
| :--- | :--- |
| **Operating System** | Ubuntu 20.04 LTS or 22.04 LTS (Recommended) |
| **Interface** | USB 3.0 Port (Required for high bandwidth) |
| **Privileges** | Root/Sudo access required for installation |
| **Internet** | Required for downloading packages and FPGA images |

---

#### Option 1: Binary Installation (Recommended)

The easiest method using the official Ettus Research Personal Package Archive (PPA). This provides stable pre-compiled binaries.

1.  **Update Repositories and Add PPA**
    ```bash
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:ettusresearch/uhd
    sudo apt update
    ```

2.  **Install UHD Host and Libraries**
    ```bash
    # Install driver, development headers, and utilities
    sudo apt install libuhd-dev uhd-host
    ```

---

#### Option 2: Building from Source (Advanced)

Recommended if you need a specific version, debugging symbols, or RFNoC support.

1.  **Install Build Dependencies**
    ```bash
    sudo apt install autoconf automake build-essential ccache cmake cpufrequtils \
    doxygen ethtool g++ git inetutils-tools libboost-all-dev libncurses5 \
    libncurses5-dev libusb-1.0-0 libusb-1.0-0-dev libusb-dev python3-dev \
    python3-mako python3-numpy python3-requests python3-setuptools python3-scipy
    ```

2.  **Clone and Build UHD**
    ```bash
    # Clone the repository
    git clone [https://github.com/EttusResearch/uhd.git](https://github.com/EttusResearch/uhd.git)
    cd uhd
    
    # Checkout the desired tag (e.g., v4.6.0.0) or stick to master
    git checkout v4.6.0.0 

    # Create build directory
    cd host
    mkdir build
    cd build

    # Configure and Compile
    cmake ../
    make -j$(nproc)
    make test
    sudo make install
    sudo ldconfig
    ```

---

#### Post-Installation Configuration (Required)

These steps are necessary for both binary and source installations to ensure the B210 is recognized and functional.

1.  **Download FPGA Images**
    The USRP B210 requires specific FPGA firmware images to operate.
    ```bash
    sudo uhd_images_downloader
    ```

2.  **Configure USB Permissions (Udev Rules)**
    Allow non-root users to access the USRP device via USB.
    ```bash
    # Copy the rules file to the system rules directory
    # Note: Path may vary slightly; if not found, check /usr/lib/uhd/utils/
    sudo cp /usr/share/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/
    
    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    ```

---

#### Verification

1.  **Connect the Device**
    Plug the USRP B210 into a **USB 3.0** port.

2.  **Run Discovery Tool**
    ```bash
    uhd_find_devices
    ```
    *Expected Output:*
    ```text
    --------------------------------------------------
    -- UHD Device 0
    --------------------------------------------------
    Device Address:
        serial: 316B...
        name: MyB210
        product: B210
        type: b200
    ```

3.  **Probe Device Capabilities**
    This loads the FPGA image and reports internal specifications.
    ```bash
    uhd_usrp_probe
    ```

---

#### Common Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **"No UHD Devices Found"** | Ensure USB 3.0 connection; Verify udev rules are applied; Re-plug device. |
| **"Loading FPGA image... failed"** | Run `sudo uhd_images_downloader` again; Check power supply (if not bus-powered). |
| **"USB 2.0 detected"** | B210 prefers USB 3.0. If using 2.0, bandwidth is limited and external power is required. |

---

#### Sources
* [Ettus Knowledge Base - Building and Installing UHD on Linux](https://kb.ettus.com/Building_and_Installing_the_USRP_Open-Source_Toolchain_(UHD_and_GNU_Radio)_on_Linux)
* [Ettus GitHub Repository - UHD](https://github.com/EttusResearch/uhd)
* [Ettus Manual - Binary Installation](https://files.ettus.com/manual/page_install.html)

#### Related Video Resource
* [USRP B210 & B200 Installation Guide](https://www.youtube.com/watch?v=ObzWYGvsGmI)

### USRP Signal Processing Theoretical and Mathematical Explanation

This document explains the nature of signals acquired from a **USRP B210**, the mathematical justification for sampling rates in complex signal processing, and a numerical comparison between real and complex sampling scenarios.

#### 1. What Signal Do We Get from a USRP?

From a USRP B210 (and most modern SDRs), you receive a **Complex Baseband Signal**, represented as **IQ Data** ($I + jQ$).

**Why Complex Baseband?**
The USRP B210 uses the Analog Devices AD9361 RFIC, which utilizes a **Zero-IF (Homodyne) Direct Conversion** architecture.

1.  **RF Signal:** The antenna receives a high-frequency real signal $r(t)$ centered at carrier frequency $f_c$ (e.g., 2.4 GHz).
2.  **Quadrature Mixing:** The device mixes $r(t)$ with two local oscillator (LO) signals that are $90^\circ$ out of phase: $\cos(2\pi f_c t)$ and $-\sin(2\pi f_c t)$.
3.  **Output:** This produces two independent streams:
    * **In-phase (I):** The real component.
    * **Quadrature (Q):** The imaginary component.
    
Mathematically, the received signal is shifted from $f_c$ down to $0$ Hz (DC). Because the signal is now centered at 0, it contains both negative and positive frequencies relative to the center. A single **Real** channel cannot distinguish between $+5$ Hz and $-5$ Hz (aliasing). A **Complex** signal ($I + jQ$) preserves this distinction, allowing us to see the full asymmetry of the spectrum.

---

#### 2. Sampling Theorem: Bandwidth vs. Max Frequency

**The User's Premise:**
> "Sampling theorem state that we need to sample at twice of maximum frequency content, it is not realated to B.W. of signal."

**Clarification:**
The standard **Nyquist-Shannon Sampling Theorem** ($F_s > 2 f_{max}$) applies strictly to **Baseband Real Signals** where the bandwidth extends from 0 to $f_{max}$.

However, for **Bandpass Signals** (like radio waves) or **Complex Signals**, the Generalized Sampling Theorem applies:
**The sampling rate $F_s$ must be greater than the total Bandwidth ($B$) of the signal, not the maximum frequency.**

$$F_s > B$$

**Why don't we sample at twice the bandwidth for USRP?**
In a USRP, we use **Complex Sampling (IQ Sampling)**. We effectively have two Analog-to-Digital Converters (ADCs) running in parallel—one for I and one for Q.
* **Real Sampling:** 1 ADC. Requires $F_s > 2B$ (to capture $0 \to B$). Effective usable bandwidth is $F_s/2$.
* **Complex Sampling:** 2 ADCs. Each ADC runs at $F_s$. Together, they provide $2 \times$ the data points. This allows us to capture the full bandwidth equal to the sample rate.
    * Usable Bandwidth = $F_s$ (ranging from $-F_s/2$ to $+F_s/2$).

---

#### 3. Numerical Example: Real vs. Complex Sampling

Let us analyze the specific example provided: A signal with spectral content existing from **-10 Hz to +10 Hz**.

**Given:**
* **Lower Frequency Limit ($f_l$):** -10 Hz
* **Upper Frequency Limit ($f_h$):** +10 Hz

##### Case A: Real Signal Processing
In the real domain, signals always have conjugate symmetry in the frequency domain ($X(f) = X^*(-f)$). If a real signal has content at +10 Hz, it fundamentally *must* have symmetric content at -10 Hz.
* **One-sided Bandwidth ($B_{real}$):** $10 \text{ Hz}$ (from 0 to 10 Hz).
* **Maximum Frequency Component ($f_{max}$):** $10 \text{ Hz}$.
* **Sampling Requirement:**
    According to Nyquist for real signals:
    $$F_s \ge 2 \cdot f_{max}$$
    $$F_s \ge 2 \cdot 10 \text{ Hz} = \mathbf{20 \text{ samples/sec}}$$
* **Result:** You need 20 samples per second to resolve 10 Hz of positive bandwidth.

##### Case B: Complex Signal Processing (USRP)
In the complex domain (IQ), symmetry is not required. The signal occupies the full span from -10 to +10 Hz.
* **Total Two-sided Bandwidth ($B_{complex}$):** $f_h - f_l = 10 - (-10) = 20 \text{ Hz}$.
* **Sampling Requirement:**
    According to the Complex Sampling Theorem (Nyquist for Complex Baseband):
    $$F_s \ge B_{total}$$
    $$F_s \ge 20 \text{ Hz}$$
* **Result:** You need **20 complex samples per second**.

##### Comparison Summary

| Feature | Real Signal | Complex Signal (USRP) |
| :--- | :--- | :--- |
| **Spectral Span** | -10 to +10 Hz (Symmetric) | -10 to +10 Hz (Asymmetric capable) |
| **Defined Bandwidth** | 10 Hz (One-sided: 0 to +10) | 20 Hz (Two-sided: -10 to +10) |
| **Nyquist Rule** | $F_s \ge 2 \times BW_{one-sided}$ | $F_s \ge 1 \times BW_{two-sided}$ |
| **Calculated $F_s$** | **20 Samples/s** | **20 Complex Samples/s** |
| **Efficiency** | Captures bandwidth equal to $F_s / 2$ | Captures bandwidth equal to $F_s$ |

**Conclusion on "Why not twice?":**
For the Complex case, we **do** sample at a rate equal to the total bandwidth (20 Hz BW $\rightarrow$ 20 Samples/s). We do *not* need $2 \times 20 = 40$ Samples/s because the "factor of 2" required by Nyquist is effectively provided by the physical hardware having two channels (I and Q) rather than one.

---
#### Sources
* **Analog Devices (AD9361 Architecture):** Explains the Zero-IF (Direct Conversion) architecture used in the USRP B210.
    * [AD9361 Datasheet & Reference](https://www.analog.com/en/products/ad9361.html)
* **Ettus Research (USRP Bandwidth):** Details on IQ sampling and bandwidth utilization.
    * [Ettus KB: USRP Bandwidth vs Sample Rate](https://kb.ettus.com/About_USRP_Bandwidths_and_Sample_Rates)
* **DSP Theory (Complex Sampling):** Richard Lyons, "Understanding Digital Signal Processing", Chapter on Quadrature Signals.
    * [DSP Related - Complex/Quadrature Sampling Explained](https://www.dsprelated.com/showarticle/192.php)
