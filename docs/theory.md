# Theory

## Table of Contents
1. [USRP](#usrp)
    - [What is USRP](#what-is-usrp)
    - [USRP B210 Technical Specifications](#usrp-b210-technical-specifications)
    - [USRP B210 Ubuntu Installation Guide UHD API](#usrp-b210-ubuntu-installation-guide-uhd-api)
    - [USRP Signal Processing Theoretical and Mathematical Explanation](#usrp-signal-processing-theoretical-and-mathematical-explanation)
    - [](#)
2. [DC Blocker](#dc-blocker)
    - [IIR DC Blocker Filter Analysis](#iir-dc-blocker-filter-analysis)
    - [DC Blocker Filter Cutoff Frequency Analysis](#dc-blocker-filter-cutoff-frequency-analysis)
    - [ DC Blocker Transient Response and Settling Time Analysis](#dc-blocker-transient-response-and-settling-time-analysis)
    - [Optimal DC Blocker Configuration](#optimal-dc-blocker-configuration)
    - [](#)
3. [STFT](#stft)
    - [Why is Windowing Needed](#why-is-windowing-needed)
    - [Why is STFT Needed](#why-is-stft-needed)
    - [STFT Formulas](#stft-formulas)
    - [Numerical Example](#numerical-example)
    - [The Spectrogram](#the-spectrogram)
    - [Spectral Leakage and Frequency Resolution](#spectral-leakage-and-frequency-resolution)
    - [The Kaiser Window](#the-kaiser-window)
    - [Optimal Beta for Kaiser Window](#optimal-beta-for-kaiser-window)
   

   
---
## USRP


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


## DC Blocker

### IIR DC Blocker Filter Analysis

This document analyzes the provided Python implementation of a First-Order IIR DC Blocker. It connects the `scipy.signal.lfilter` coefficients to the underlying difference equation and provides a numerical step-by-step trace to demonstrate how DC offset is removed.

#### 1. Mathematical Foundation

The code implements a classic First-Order IIR High-Pass Filter used for DC removal.

**Transfer Function:**
The transfer function $H(z)$ is defined as:

$$H(z) = \frac{Y(z)}{X(z)} = \frac{1 - z^{-1}}{1 - \alpha z^{-1}}$$

**Difference Equation:**
By applying the inverse Z-transform, we derive the time-domain difference equation used for calculation:

$$y[n] = x[n] - x[n-1] + \alpha \cdot y[n-1]$$

**Mapping to Python (`lfilter`):**
The `scipy.signal.lfilter` function solves difference equations using coefficient arrays `b` (numerator) and `a` (denominator).
* **Numerator (`b`):** $[1, -1]$ corresponds to $1 - z^{-1}$ (Terms: $x[n] - x[n-1]$).
* **Denominator (`a`):** $[1, -\alpha]$ corresponds to $1 - \alpha z^{-1}$ (Terms: $y[n] - \alpha y[n-1]$).

---

#### 2. Numerical Trace: Removing a Constant DC Offset



We track the filter's behavior manually to verify DC removal.

**Scenario:**
* **Input ($x$):** A constant DC signal of **10** (e.g., 10V DC offset).
* **Alpha ($\alpha$):** Set to **0.5** for simplified math.
* **Initial State:** Assume $x[-1] = 0$ and $y[-1] = 0$.

**Trace Table:**

| Step ($n$) | Current Input ($x[n]$) | Previous Input ($x[n-1]$) | Previous Output ($y[n-1]$) | Calculation ($x[n] - x[n-1] + 0.5 \cdot y[n-1]$) | Output ($y[n]$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | 10 | 0 | 0 | $10 - 0 + (0.5 \times 0)$ | **10.0** |
| **1** | 10 | 10 | 10 | $10 - 10 + (0.5 \times 10)$ | **5.0** |
| **2** | 10 | 10 | 5 | $10 - 10 + (0.5 \times 5)$ | **2.5** |
| **3** | 10 | 10 | 2.5 | $10 - 10 + (0.5 \times 2.5)$ | **1.25** |
| **4** | 10 | 10 | 1.25 | $10 - 10 + (0.5 \times 1.25)$ | **0.625** |
| ... | ... | ... | ... | ... | ... |
| **$\infty$** | 10 | 10 | ~0 | $10 - 10 + (0.5 \times 0)$ | **0.0** |

##### Analysis of the Trace
1.  **Step 0 (The Spike):** The filter initially outputs **10**. This is the **Transient Response**. The filter has not yet "learned" that the 10 is constant; it looks like a new step change.
2.  **Steps 1-4 (The Decay):** The term $(x[n] - x[n-1])$ becomes $(10 - 10 = 0)$. This is the mechanism that "blocks" the DC. A constant value has a difference of zero.
3.  **The Memory Effect:** The output stays non-zero briefly because of the feedback term $+ \alpha \cdot y[n-1]$. With $\alpha=0.5$, the residual error is halved every step.
4.  **Convergence:** The value rapidly approaches 0. The DC offset is removed.

---
If we had used alpha=0.99, the value would shrink by 0.99 every time. It would take much longer to reach 0 (a longer transient), but the filter would be much sharper, preserving signals that are near DC (like 1Hz or 2Hz) much better than alpha=0.5.

This is why the code includes return filtered[1000:]—to cut off that initial period where the value is dropping from 10 down to 0.

---

#### Sources
* **Filter Design Theory:** Smith, J.O. "Introduction to Digital Filters with Audio Applications", *Stanford University*. [Link to Chapter on DC Blockers](https://ccrma.stanford.edu/~jos/fp/DC_Blocker.html)
* **Implementation Reference:** SciPy.org, "scipy.signal.lfilter Documentation". [Link to SciPy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
* **Practical DSP:** "The Scientist and Engineer's Guide to Digital Signal Processing", *Steven W. Smith*. [Link to Chapter 19: Recursive Filters](https://www.dspguide.com/ch19.htm)

### DC Blocker Filter Cutoff Frequency Analysis

The following documentation details the mathematical derivation for the cutoff frequency of a First-Order IIR DC Blocker filter. The derivation tracks the transition from the difference equation to the exact frequency response, and subsequently to a simplified approximation for implementation constraints.

**Filter Definition:**
The filter is defined by the difference equation:
$$y(n) = x(n) - x(n-1) + \alpha y(n-1)$$

Where $\alpha$ is the pole location, typically close to 1 (e.g., 0.995).

---

#### 1. Exact Cutoff Frequency Derivation

The exact cutoff frequency is derived by analyzing the pole-zero plot and frequency response of the system transfer function.

**Step 1: Transfer Function Determination**
Taking the Z-transform of the difference equation:
$$Y(z) = X(z) - X(z)z^{-1} + \alpha Y(z)z^{-1}$$

Rearranging to solve for the transfer function $H(z) = \frac{Y(z)}{X(z)}$:
$$Y(z)(1 - \alpha z^{-1}) = X(z)(1 - z^{-1})$$
$$H(z) = \frac{1 - z^{-1}}{1 - \alpha z^{-1}}$$

**Step 2: Frequency Response**
Substituting $z = e^{j\theta}$ (where $\theta$ is the normalized frequency $\omega T$):
$$H(\theta) = \frac{1 - e^{-j\theta}}{1 - \alpha e^{-j\theta}}$$

Using Euler's Identity ($e^{-j\theta} = \cos\theta - j\sin\theta$) and separating real and imaginary parts:
$$H(\theta) = \frac{(1 - \cos\theta) + j\sin\theta}{(1 - \alpha\cos\theta) + j\alpha\sin\theta}$$

**Step 3: Magnitude Squared Response**
The squared magnitude $|H(\theta)|^2$ is calculated as:
$$|H(\theta)|^2 = \frac{(1 - \cos\theta)^2 + (\sin\theta)^2}{(1 - \alpha\cos\theta)^2 + (\alpha\sin\theta)^2}$$

Expanding and applying the identity $\cos^2\theta + \sin^2\theta = 1$:
$$|H(\theta)|^2 = \frac{1 - 2\cos\theta + \cos^2\theta + \sin^2\theta}{1 - 2\alpha\cos\theta + \alpha^2\cos^2\theta + \alpha^2\sin^2\theta}$$
$$|H(\theta)|^2 = \frac{2 - 2\cos\theta}{1 + \alpha^2 - 2\alpha\cos\theta}$$

**Step 4: Maximum Gain Calculation**
To define the cutoff (-3dB point), we first identify the maximum gain. Differentiating with respect to $\theta$ reveals the maximum occurs at the Nyquist frequency $\theta = \pi$:
$$|H(\pi)|^2 = \frac{2 - 2(-1)}{1 + \alpha^2 - 2\alpha(-1)} = \frac{4}{(1+\alpha)^2}$$
$$\therefore |H(\theta)|_{\text{max}} = \frac{2}{1+\alpha}$$

**Step 5: Exact Cutoff Formula**
The cutoff frequency $\theta_c$ is defined where the gain drops to $\frac{1}{\sqrt{2}}$ of the maximum:
$$|H(\theta_c)|^2 = \frac{1}{2} |H(\theta)|_{\text{max}}^2$$

Substituting the derived expressions:
$$\frac{2 - 2\cos\theta_c}{1 + \alpha^2 - 2\alpha\cos\theta_c} = \frac{1}{2} \left( \frac{4}{(1+\alpha)^2} \right)$$

Through algebraic simplification (cross-multiplying and solving for $\cos\theta_c$), we obtain the condition:
$$\cos\theta_c = \frac{2\alpha}{1+\alpha^2}$$

Converting normalized frequency $\theta_c$ to Hz ($f_c$):
$$f_c = \frac{f_s}{2\pi} \cos^{-1}\left( \frac{2\alpha}{1+\alpha^2} \right)$$

---

#### 2. Approximate Cutoff Frequency Derivation

For DSP implementations where $\alpha \approx 1$, a simplified linear approximation is often required to avoid computationally expensive inverse cosine functions.

**Step 1: Small Angle Assumption**
Let $\alpha = 1 - \epsilon$, where $\epsilon$ is a very small number ($\epsilon \to 0$).
Substituting this into the exact condition $\cos\theta_c = \frac{2\alpha}{1+\alpha^2}$:

$$\frac{2(1-\epsilon)}{1 + (1-\epsilon)^2} = \frac{2 - 2\epsilon}{1 + (1 - 2\epsilon + \epsilon^2)} = \frac{2 - 2\epsilon}{2 - 2\epsilon + \epsilon^2}$$

**Step 2: Taylor Series Approximation**
Dividing the numerator and denominator by 2 (and ignoring the negligible $\epsilon^2$ term in the denominator for the first-order approximation):
$$\approx \frac{1 - \epsilon}{1 - \epsilon} \quad \text{(This is too rough, we need higher precision)}$$

Instead, we use the property that for small $x$, $\cos(x) \approx 1 - \frac{x^2}{2}$.
We manipulate the fraction:
$$\frac{2 - 2\epsilon}{2 - 2\epsilon + \epsilon^2} = 1 - \frac{\epsilon^2}{2 - 2\epsilon + \epsilon^2}$$

Since $\epsilon$ is small, the denominator $2 - 2\epsilon + \epsilon^2 \approx 2$. Thus:
$$\text{RHS} \approx 1 - \frac{\epsilon^2}{2}$$

**Step 3: Equating Approximations**
We now have:
$$\cos(\theta_c) \approx 1 - \frac{\epsilon^2}{2}$$

Comparing this to the Taylor expansion of cosine ($\cos(\theta) \approx 1 - \frac{\theta^2}{2}$):
$$\theta_c \approx \epsilon$$

**Step 4: Final Approximate Formula**
Substituting $\theta_c = 2\pi \frac{f_c}{f_s}$ and $\epsilon = 1 - \alpha$:
$$2\pi \frac{f_c}{f_s} \approx 1 - \alpha$$

$$f_c \approx \frac{f_s}{2\pi}(1 - \alpha)$$

---

#### Summary of Results

| Parameter | Formula |
| :--- | :--- |
| **Transfer Function** | $H(z) = \frac{1 - z^{-1}}{1 - \alpha z^{-1}}$ |
| **Exact Cutoff** | $f_c = \frac{f_s}{2\pi} \cos^{-1}\left( \frac{2\alpha}{1+\alpha^2} \right)$ |
| **Approximate Cutoff** | $f_c \approx \frac{f_s}{2\pi}(1 - \alpha)$ |

---

#### Sources
* [cite_start]**IIR FILTER.pdf** (Provided User Document) - *Pages 1-3* [cite: 62-82]
    * Derivation of exact transfer function and maximum gain.
* [cite_start]**Filter approximate cutoff frequency.pdf** (Provided User Document) - *Pages 1-2* [cite: 1-21]
    * Derivation of small-angle approximation using Taylor series.


### DC Blocker Transient Response and Settling Time Analysis

The implementation of an Infinite Impulse Response (IIR) DC blocker introduces a critical time-domain constraint known as **Settling Time**. This is the duration required for the filter's internal state to stabilize after initialization or a sudden change in input.

#### 1. The Concept of Settling Time
An IIR filter, by definition, uses feedback ($\alpha$) to process signals. This feedback creates a "memory" effect where the output depends on previous outputs. When the filter is first started (or encounters a step change), it produces a **Transient Response**—a temporary period of distorted output before it reaches its steady-state behavior.

#### 2. Time Constant ($\tau$) Calculation
The duration of this transient response is governed by the filter's **Time Constant** ($\tau$), which is inversely proportional to the distance of the pole ($\alpha$) from the unit circle.

For a first-order IIR filter with a pole at $\alpha$ (where $\alpha \approx 1$), the time constant in samples is approximated by the standard DSP formula:

$$\tau \approx \frac{1}{1 - \alpha}$$

* **$\tau$ (Tau):** The number of samples it takes for the transient error to decay to approx 36.8% ($1/e$) of its initial value.
* **$\alpha$ (Alpha):** The filter coefficient. As $\alpha \to 1$, the denominator $(1-\alpha) \to 0$, causing $\tau$ to increase rapidly.

#### 3. The 5$\tau$ Stability Rule
In control theory and signal processing, a system is generally considered "settled" (or stable enough for accurate measurement) after approximately **5 Time Constants**.

$$\text{Settling Time} \approx 5 \times \tau$$

At $5\tau$, the transient error has decayed to less than 1% ($e^{-5} \approx 0.0067$), making the data reliable for processing.

#### 4. Critical Code Conflict: Discarding Samples
The provided code snippet includes a hardcoded discard limit: `filtered[1000:]`. This creates a potential data integrity risk if the filter's physics conflicts with this arbitrary number.

* **The Conflict:** If the chosen $\alpha$ results in a Settling Time ($5\tau$) that is greater than the number of discarded samples ($N_{discard}$), the user will receive corrupted data containing transient artifacts.
* **The Condition:** Data is valid only if:
    $$N_{discard} > \frac{5}{1 - \alpha}$$

If this condition is not met, the initial chunk of the returned signal will be distorted "garbage" data rather than the true signal.

#### 5. Optimization & Trade-offs
There is an inherent trade-off between frequency resolution and time-domain performance.

| Parameter | Effect of Increasing $\alpha$ (closer to 1.0) | Effect of Decreasing $\alpha$ (further from 1.0) |
| :--- | :--- | :--- |
| **Cutoff Frequency** | **Lower (Better):** Removes only DC; preserves low freq signals. | **Higher (Worse):** May attenuate useful low freq bass/signals. |
| **Settling Time** | **Slower (Worse):** Filter takes longer to stabilize. | **Faster (Better):** Filter stabilizes quickly. |
| **Data Loss** | **High:** Requires discarding more initial samples. | **Low:** Requires discarding fewer initial samples. |

**Final Recommendation:**
To ensure data integrity, the number of discarded samples in the code must be dynamically calculated based on $\alpha$, or $\alpha$ must be tuned such that $5\tau$ fits within the fixed discard limit.

---
##### Sources
* [DSPRelated - DC Blocker Introduction & Time Constants](https://www.dsprelated.com/freebooks/filters/DC_Blocker.html)
* [DSPRelated - Calculating Time Constants for IIR Filters](https://www.dsprelated.com/showthread/comp.dsp/5126-1.php)
* [DSP StackExchange - Trade-off between DC removal and Settling Time](https://dsp.stackexchange.com/questions/74237/how-to-implement-a-high-pass-filter-digitally-to-remove-the-dc-offset-from-senso)
* [ETH Zurich - Signals and Systems Lecture 9 (IIR Properties)](https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/Lectures/Signals-and-Systems/Lectures/Fall2018/Lecture9_sigsys.pdf)

 
### Optimal DC Blocker Configuration

The design of a First-Order IIR DC Blocker requires balancing two competing requirements: **Frequency Resolution** (preserving low-frequency signals) and **Transient Response** (minimizing the data lost to filter settling). This balance is controlled by the pole location parameter, **Alpha ($\alpha$)**.

#### 1. The DC Blocker Transfer Function

The standard recursive (IIR) DC blocker is defined by the difference equation:

$$y[n] = x[n] - x[n-1] + \alpha \cdot y[n-1]$$

Its transfer function in the Z-domain is:

$$H(z) = \frac{1 - z^{-1}}{1 - \alpha z^{-1}}$$

Where:
* **Zero at $z=1$ (DC):** Forces the gain at 0 Hz to be zero.
* **Pole at $z=\alpha$:** Determines how "sharp" the notch is. As $\alpha \to 1$, the notch becomes narrower, preserving more low-frequency signal but increasing the settling time.

---

#### 2. Determining Optimal Alpha ($\alpha$)

To find the "optimal" $\alpha$, we map the filter's **-3dB Cutoff Frequency ($f_c$)** to the pole location. The goal is to set $f_c$ below the lowest frequency component of interest (e.g., your resolution limit).

**The Mathematical Derivation:**
For low-frequency cutoffs ($f_c \ll f_s$), the relationship between the -3dB cutoff frequency and $\alpha$ is approximated by the small-angle approximation of the unit circle on the Z-plane.

$$f_c \approx \frac{f_s (1 - \alpha)}{2\pi}$$

Rearranging to solve for $\alpha$:

$$\alpha_{optimal} \approx 1 - \frac{2\pi f_c}{f_s}$$

* **$f_c$ (Cutoff Frequency):** The frequency where the signal is attenuated by 3dB. Signals below this are blocked.
* **$f_s$ (Sampling Rate):** The rate at which the USRP is capturing data.

**Constraint:**
If you require a frequency resolution of 25 kHz, you typically set $f_c$ to be a fraction of that (e.g., 10% or exactly equal depending on tolerance) to ensure the 25 kHz signal is not significantly attenuated.

---

#### 3. Calculating Discarded Samples (Settling Time)

IIR filters have "infinite" memory, meaning their output depends on previous states. When the filter starts, it encounters a "step input" (the DC offset). It takes time for the internal state to rise from 0 to match this offset. This period is called the **Transient Response**.

**The Time Constant ($\tau$):**
The speed at which the filter settles is governed by its decay time constant, measured in samples:

$$\tau \approx \frac{1}{1 - \alpha} \quad \text{(samples)}$$

**The 5-Tau Rule:**
In linear systems theory, a system is considered "settled" (within ~0.7% of the final value) after **5 Time Constants**.

$$N_{discard} \approx 5 \times \tau = \frac{5}{1 - \alpha}$$

* **At $1\tau$:** 63.2% settled.
* **At $3\tau$:** 95.0% settled.
* **At $5\tau$:** 99.3% settled (Standard engineering safety margin).

---

#### 4. Summary Calculation Workflow

To implement this dynamically in software for a USRP B210:

| Step | Parameter | Formula |
| :--- | :--- | :--- |
| **1** | **Target Cutoff ($f_c$)** | Defined by user needs (e.g., 25 kHz or $0.1 \times$ Resolution). |
| **2** | **Optimal Alpha ($\alpha$)** | $\alpha = 1 - \frac{2\pi f_c}{f_s}$ |
| **3** | **Time Constant ($\tau$)** | $\tau = \frac{1}{1 - \alpha}$ |
| **4** | **Samples to Discard** | $N = \lceil 5 \times \tau \rceil$ |

#### Numerical Example
* **Scenario:** $f_s = 20 \text{ MHz}$, Target $f_c = 25 \text{ kHz}$.
1.  **Calculate Alpha:**
    $$\alpha = 1 - \frac{2\pi \times 25000}{20000000} = 1 - 0.00785 = \mathbf{0.99215}$$
2.  **Calculate Time Constant:**
    $$\tau = \frac{1}{1 - 0.99215} \approx 127 \text{ samples}$$
3.  **Calculate Discard Count:**
    $$N_{discard} = 5 \times 127 = \mathbf{635 \text{ samples}}$$

---

#### Sources
* **J.O. Smith III, "Introduction to Digital Filters with Audio Applications", Stanform University.**
    * *Topic:* DC Blocker difference equation and pole placement.
    * [Link to Text](https://ccrma.stanford.edu/~jos/fp/DC_Blocker.html)
* **Richard G. Lyons, "Understanding Digital Signal Processing".**
    * *Topic:* IIR Filter transient response and settling time ($5\tau$ rule).
    * [Link to Book Info](https://www.dsprelated.com/freebooks/filters/Transient_Response.html)
* **Analog Devices, "Linear Circuit Design Handbook", Chapter 8.**
    * *Topic:* Relationship between cutoff frequency and time constant.
    * [Link to Handbook](https://www.analog.com/en/education/education-library/linear-circuit-design-handbook.html)

## STFT

### Why is Windowing Needed

Windowing is required primarily because the Discrete Fourier Transform (DFT) can only process signals of **finite length**, whereas many real-world signals (like speech or radar) are indefinitely long.

* **Finite Duration Requirement:** To use the DFT, we must select a finite-length segment of the signal $x[n]$. This is done by multiplying the signal by a window sequence $w[n]$ that is zero outside a specific range.
* **Spectral Leakage Control:** A simple truncation (rectangular window) causes "smearing" of energy in the frequency domain, known as **leakage**. This happens because the abrupt edges of a rectangular window create large side lobes in its frequency response.
* **Smoothing:** Applying a tapered window (like a Hamming or Kaiser window) smooths the edges of the signal segment. This reduces the side lobes in the frequency domain, allowing for better distinction between sinusoidal components that have different amplitudes, though it effectively widens the main peak (reducing resolution slightly).

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.1, pp. 793-795; [cite_start]Section 10.2.1 "The Effect of Windowing", pp. 797-800[cite: 1, 4].

---

### Why is STFT Needed

The standard Fourier transform (or a single long DFT) is insufficient for **nonstationary signals**, whose properties change over time.

* **Time-Varying Properties:** Signals like speech, radar, or linear chirps have frequencies that vary with time. A single DFT over a long duration averages these frequency components together, losing the information about *when* specific frequencies occurred.
* **Tracking Changes:** To analyze these changes, we need a method that tracks frequency content as a function of time. The STFT achieves this by computing the Fourier transform of short, overlapping segments of the signal as the window slides past the signal.
* **Trade-off:** A shorter window provides better time resolution (we know better *when* an event happened) but poorer frequency resolution (we know less precisely *what* frequency it is), and vice versa.

> [cite_start]**Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.3 "The Time-Dependent Fourier Transform", pp. 811-814[cite: 4].

---

### STFT Formulas

The STFT is formally referred to in the text as the **Time-Dependent Fourier Transform**.

#### Continuous Frequency Definition
The fundamental formula for the time-dependent Fourier transform is:

$$X[n, \lambda) = \sum_{m=-\infty}^{\infty} x[n+m]w[m]e^{-j \lambda m}$$

* **$n$**: The discrete time index where the window is positioned.
* **$\lambda$**: The continuous frequency variable (radians).
* **$x[n+m]$**: The signal shifted in time.
* **$w[m]$**: The window sequence (stationary relative to $m$).

> **Source:** Eq. (10.18), Chapter 10, Section 10.3, p. [cite_start]811[cite: 4].

#### Discrete STFT (Sampled Frequency)
In practice, we compute the transform at discrete frequency samples $\lambda_k = \frac{2\pi k}{N}$ using the DFT. This creates a sampled spectrum $X[n, k]$.

If the window $w[m]$ has a finite length $L$ (nonzero for $0 \le m \le L-1$) and we use a DFT of length $N$ (where $N \ge L$):

$$X[n, k] = \sum_{m=0}^{L-1} x[n+m]w[m]e^{-j \frac{2\pi}{N} k m}, \quad k = 0, 1, \dots, N-1$$

* **Overlap:** The parameter $n$ is typically advanced by a step size $R$ (often called the hop size) rather than 1. This creates overlap between consecutive analysis windows. If window length is $L$ and step is $R < L$, the overlap is $L-R$ samples.

> **Source:** Derived from Eq. (10.18) and the definition of DFT in Eq. (10.3) [cite_start]and Section 10.3 discussion[cite: 4].

#### Discrete STFT (Sampled in both time and frequency) 

The specific formula provided represents the **Discrete Short-Time Fourier Transform** sampled in both time and frequency. In the text, the general Time-Dependent Fourier Transform is defined as $X[n, \lambda)$. When sampled at discrete frequencies $\lambda_k = 2\pi k/N$ and discrete time intervals $n = rR$, it becomes:

$$X[rR, k] = \sum_{m=0}^{L-1} x[rR + m]w[m]e^{-j \frac{2\pi}{N} k m}$$

#### Detailed Component Analysis

* **$X[rR, k]$**: The STFT value at block index $r$ and frequency bin $k$.
* **$r$**: The integer index of the time frame (or block).
* **$R$**: The **temporal decimation factor** or **hop size**. It represents the number of samples the window slides between consecutive frames.
    * If $R < L$, the windows overlap.
    * If $R = L$, there is no overlap.
* **$rR$**: The starting sample index of the current analysis window in the global signal $x[n]$.
* **$m$**: The local time index inside the window, ranging from $0$ to $L-1$.
* **$x[rR + m]$**: The segment of the signal currently being analyzed. It selects samples starting from $rR$.
* **$w[m]$**: The window sequence (e.g., Hamming, Rectangular) of length $L$, which is stationary relative to the local index $m$.
* **$e^{-j \frac{2\pi}{N} k m}$**: The complex exponential basis function of the DFT. Note that the phase depends on the local index $m$, meaning the phase reference is the start of the current window.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.3, "The Time-Dependent Fourier Transform". The sampling in time and frequency is discussed following Eq. (10.18).

---

### Numerical Example

We will calculate the STFT for a linearly increasing signal.

**Parameters:**
* **Signal ($x[n]$):** $\{ 1, 2, 3, 4, 5, \dots \}$
* **Window ($w[m]$):** Rectangular of length **$L=4$** ($w = \{1, 1, 1, 1\}$).
* **DFT Length ($N$):** 4.
* **Hop Size ($R$):** 1.
    * **Overlap:** $L - R = 4 - 1 = 3$ samples.
    * **Percentage:** $3/4 = \mathbf{75\%}$.

**Objective:** Calculate $X[rR, k]$ for time blocks $r=0$ and $r=1$.

#### Step 1: Time Block $r=0$
* **Start Index ($rR$):** $0 \times 1 = 0$.
* **Segment $x[0+m]$:** $\{1, 2, 3, 4\}$.
* **Windowed Segment:** $\{1, 2, 3, 4\}$ (since $w[m]=1$).

**4-Point DFT Calculation ($N=4$):**
Using $W_4^0 = 1, W_4^1 = -j, W_4^2 = -1, W_4^3 = j$.

* **$k=0$ (DC):**
    $$1 + 2 + 3 + 4 = \mathbf{10}$$
* **$k=1$:**
    $$1(1) + 2(-j) + 3(-1) + 4(j) = 1 - 2j - 3 + 4j = \mathbf{-2 + 2j}$$
* **$k=2$:**
    $$1(1) + 2(-1) + 3(1) + 4(-1) = 1 - 2 + 3 - 4 = \mathbf{-2}$$
* **$k=3$:**
    $$1(1) + 2(j) + 3(-1) + 4(-j) = 1 + 2j - 3 - 4j = \mathbf{-2 - 2j}$$

**Result $X[0, k]$:** $\{10, -2+2j, -2, -2-2j\}$

---

#### Step 2: Time Block $r=1$
* **Start Index ($rR$):** $1 \times 1 = 1$.
* **Segment $x[1+m]$:** $\{2, 3, 4, 5\}$.
    *(Notice the substantial overlap with the previous segment)*
* **Windowed Segment:** $\{2, 3, 4, 5\}$.

**4-Point DFT Calculation:**

* **$k=0$ (DC):**
    $$2 + 3 + 4 + 5 = \mathbf{14}$$
* **$k=1$:**
    $$2(1) + 3(-j) + 4(-1) + 5(j) = 2 - 3j - 4 + 5j = \mathbf{-2 + 2j}$$
* **$k=2$:**
    $$2(1) + 3(-1) + 4(1) + 5(-1) = 2 - 3 + 4 - 5 = \mathbf{-2}$$
* **$k=3$:**
    $$2(1) + 3(j) + 4(-1) + 5(-j) = 2 + 3j - 4 - 5j = \mathbf{-2 - 2j}$$

**Result $X[1, k]$:** $\{14, -2+2j, -2, -2-2j\}$

---

#### Observation
Comparing $r=0$ and $r=1$, the AC components ($k=1, 2, 3$) remained identical because the "shape" of the ramp (a slope of 1) did not change, only its DC offset increased by 4 (the difference between $x[n]$ and $x[n-1]$ accumulated over 4 samples). This demonstrates how the STFT tracks spectral properties over time.

### The Spectrogram

This document explains the concept of a spectrogram, its axes, and the information it conveys, based on **Chapter 10** of *Discrete-Time Signal Processing* by Oppenheim and Schafer (3rd Edition).

---

#### 1. Definition and Quote

A spectrogram is a visual representation of the Short-Time Fourier Transform (STFT) magnitude. As defined in the text:

> "This display, which shows $20 \log_{10} |X[n, \lambda)|$ as a function of $\lambda/2\pi$ in the vertical dimension, and the time index $n$ in the horizontal dimension is called a **spectrogram**."

*Note: The quote in the text refers to the signal transform $X[n, \lambda)$ (or $Y[n, \lambda)$ depending on context of the specific figure being discussed).*

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.3, p. 817 (describing Figure 10.12).

---

#### 2. Axes and Structure

The spectrogram maps a three-dimensional function (magnitude vs. time vs. frequency) onto a two-dimensional plane.

* **Horizontal Axis (Time):**
    * Represents the time index $n$ (or sample number).
    * As you move from left to right, you are observing the evolution of the signal over time.
    * The time axis corresponds to the sliding position of the analysis window.

* **Vertical Axis (Frequency):**
    * Represents the normalized frequency $\lambda/2\pi$ (or sometimes analog frequency if the sampling rate is known).
    * Commonly ranges from $0$ to $0.5$ (representing $0$ to the Nyquist frequency, $\pi$).
    * As you move from bottom to top, the frequency increases.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.3, text surrounding Figure 10.12.

---

#### 3. Information Provided

The spectrogram provides a "time-frequency" view of a signal, allowing us to see how the spectral content changes over time.

* **Intensity/Color (Magnitude):**
    * Since the display is 2D, the third dimension—the magnitude of the transform $|X[n, \lambda)|$—is represented by the darkness, brightness, or color of the point $(n, \lambda)$.
    * The value is typically plotted on a logarithmic scale ($20 \log_{10}$) to compress the dynamic range, making it easier to see low-level spectral components alongside strong ones.
    * **Dark/Colored Areas:** Indicate high energy or strong frequency components at that specific time and frequency.
    * **Light/Background Areas:** Indicate low energy or silence.

* **Key Insights:**
    * It allows identification of **nonstationary** features, such as chirps (frequencies changing linearly), speech formants, or transient pulses.
    * It reveals the trade-off between time and frequency resolution: a wide window (long time duration) gives narrow frequency bands (good frequency resolution) but blurs time details (poor time resolution), and vice versa.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.3, pp. 817-819.

### Spectral Leakage and Frequency Resolution

#### 1. Spectral Leakage

**Definition:**
Spectral leakage is the phenomenon where energy from a signal at a specific frequency "leaks" into adjacent frequencies in the spectrum. This "smearing" of spectral energy makes it difficult to distinguish weak signals in the presence of strong ones.

**Why it happens:**
In practical spectral analysis, we cannot analyze an infinite-duration signal. We must limit the signal to a finite duration using a **window** sequence $w[n]$. This operation in the time domain is a multiplication:

$$v[n] = x[n]w[n]$$

where $x[n]$ is the signal and $v[n]$ is the windowed segment.

According to the **Modulation (or Windowing) Theorem**, multiplication in the time domain corresponds to **periodic convolution** in the frequency domain. The Fourier transform of the windowed signal, $V(e^{j\omega})$, is the convolution of the signal's spectrum $X(e^{j\theta})$ and the window's spectrum $W(e^{j\omega})$:

$$V(e^{j\omega}) = \frac{1}{2\pi} \int_{-\pi}^{\pi} X(e^{j\theta})W(e^{j(\omega-\theta)}) d\theta$$

Ideally, the window's spectrum $W(e^{j\omega})$ would be an impulse (delta function), which would perfectly reproduce $X(e^{j\omega})$. However, finite-duration windows have a continuous spectrum consisting of a **main lobe** and **side lobes**.
* When the window's spectrum is convolved with the signal's spectral peaks (impulses), the **side lobes** of the window cause the energy to spread (leak) into frequencies far away from the center frequency.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.1, Eq. (10.2), and Section 10.2.1 "The Effect of Windowing", pp. 795, 797-800.

---

#### 2. Frequency Resolution

**Definition:**
Frequency resolution is the ability to resolve (distinguish) two distinct sinusoidal signal components that are closely spaced in frequency.

**How it works:**
Resolution is determined primarily by the **width of the main lobe** of the window's spectrum $W(e^{j\omega})$.
* If two frequency components, $\omega_0$ and $\omega_1$, are very close to each other, the main lobes of the window centered at these frequencies will overlap.
* If the overlap is significant, the two distinct peaks may merge into a single peak in the resulting spectrum $|V(e^{j\omega})|$, making it impossible to tell that there are two separate signals.
* To resolve two frequencies, the difference $|\omega_1 - \omega_0|$ must generally be larger than the width of the main lobe.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.2.2 "Properties of the Windows", p. 800.

---

#### 3. The Trade-off

There is a fundamental trade-off between minimizing spectral leakage and maximizing frequency resolution. This is controlled by the shape and length of the window $w[n]$.

#### The Conflict
1.  **Main Lobe Width (Resolution):** To distinguish close frequencies, we need a **narrow main lobe**.
2.  **Side Lobe Amplitude (Leakage):** To prevent strong signals from masking weak ones (leakage), we need **low amplitude side lobes**.

#### Comparison of Windows
* **Rectangular Window:**
    * Has the **narrowest main lobe** for a given length $L$ (approximate width $\Delta_{ml} = 4\pi/L$).
    * **Best Frequency Resolution**.
    * Has the **highest side lobes** (the first side lobe is only about 13 dB down from the main peak).
    * **Worst Spectral Leakage**.

* **Tapered Windows (e.g., Hamming, Hann, Bartlett):**
    * These windows taper smoothly to zero at the edges, which reduces the discontinuities.
    * This **reduces side lobe levels** significantly (e.g., Hamming side lobes are ~41 dB down).
    * **Low Spectral Leakage**.
    * However, this comes at the cost of a **wider main lobe** (approximate width $\Delta_{ml} = 8\pi/L$ for Hamming/Hann).
    * **Poorer Frequency Resolution** (for the same window length).

#### Summary of Trade-off
You cannot optimize both simultaneously simply by changing the window shape.
* If you choose a window to reduce leakage (tapered), you widen the main lobe and lose resolution.
* If you choose a window to improve resolution (rectangular), you raise the side lobes and increase leakage.
* The **Kaiser Window** is a special window that includes a parameter $\beta$ to allow the user to continuously trade off between main-lobe width and side-lobe amplitude.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.2.2, pp. 800-801; Chapter 7, Section 7.5.1, pp. 535-538.

### The Kaiser Window

#### 1. Difference from Other Windows

The fundamental difference between the **Kaiser window** and other commonly used windows (such as the Rectangular, Bartlett, Hann, Hamming, and Blackman windows) lies in the **controllability of the window's properties**.

* **Standard Windows (e.g., Hamming, Hann):** These windows have a fixed shape. They have only one parameter: the length **$L$** (or $M$).
    * Changing the length $L$ affects the **width of the main lobe** (frequency resolution).
    * However, the **relative side-lobe amplitude** (leakage) is fixed for each window type. For example, a Rectangular window always has side lobes about 13 dB down, and a Hamming window always has side lobes about 41 dB down, regardless of their length. You cannot trade off main-lobe width for lower side lobes with a fixed window type.
* **Kaiser Window:** The Kaiser window relies on **two parameters**: the length **$L$** (or $M$) and a shape parameter **$\beta$** (beta).
    * This allows you to independently control the **main-lobe width** and the **side-lobe amplitude**.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 10, Section 10.2.2, p. 800; Chapter 7, Section 7.5.3, p. 541.

---

#### 2. Advantage of Using the Kaiser Window

The primary advantage of the Kaiser window is its **flexibility** and the existence of **simple empirical formulas** for design.

* **Adjustable Trade-off:** By varying the parameter $\beta$, a designer can continuously trade off between the main-lobe width (resolution) and the side-lobe amplitude (leakage).
    * If $\beta = 0$, it becomes a Rectangular window (narrowest main lobe, highest side lobes).
    * As $\beta$ increases, the side lobes decrease in amplitude, but the main lobe becomes wider.
* **Near-Optimal Performance:** The Kaiser window approximates the *prolate spheroidal wave functions*, which are theoretically optimal in maximizing energy concentration in the main lobe.
* **Direct Design:** Using the formulas , one can calculate the exact length $L$ and shape $\beta$ required to meet specific filter specifications (like stopband attenuation and transition width), avoiding trial-and-error methods.

> **Source:** *Discrete-Time Signal Processing*, 3rd Ed., Chapter 7, Section 7.5.3, p. 541; Chapter 10, Section 10.2.2, p. 801.

### Optimal Beta for Kaiser Window

#### 1. Dynamic Range of an ADC

**Definition:**
From a signal processing perspective (Chapter 6), the dynamic range of an ADC is determined by its **Signal-to-Quantization-Noise Ratio (SQNR)**. It represents the ratio between the maximum possible signal amplitude (Full Scale) and the quantization noise floor introduced by the finite number of bits.

For a $(B+1)$-bit quantizer (or $B$ bits plus sign), the dynamic range (SNR) is approximately:
$$SNR \approx 6.02B + 1.76 \text{ dB}$$

* **Full Scale (0 dB):** The maximum amplitude the ADC can ingest without clipping (saturation).
* **Noise Floor:** The limit imposed by quantization error. Signals below this level are indistinguishable from quantization noise.
* **Role in SDR:** In a Software Defined Radio, this defines the weakest signal you can detect in the presence of a strong signal filling the ADC's range.

> **Source:** Eq. (6.33), Chapter 6, Section 6.3.2, p. 493.

---

#### 2. Relation to Spectral Leakage (Adapted Visual Explanation)

Using the requested analogy structure adapted to Signal Processing terms:

* **0 dB Reference (Surface):** This represents **0 dBFS (Full Scale)**. Strong signals, like a high-power local transmitter, reach near this level.
* **ADC Noise Floor (The "True" Bottom):** This is the **-78 dB** limit (for your specific USRP case). It represents the quantization noise floor. The FFT cannot detect physical signals below this level because they are buried in quantization noise.
* **Window Side Lobe Level (The Artificial Floor):** This is the attenuation of the window's side lobes (e.g., -60 dB).
* **The Shadow Effect (Leakage):**
    * If you use a window with side lobes at **-60 dB**, a strong signal at 0 dB will generate "spectral leakage" side lobes that extend down to -60 dB.
    * A weak signal existing at **-70 dB** is physically detectable by the ADC (since -70 > -78).
    * However, it will be **masked** (hidden) by the -60 dB side lobes of the strong signal. The "math noise" (leakage) effectively raises the noise floor above the hardware's capability.
* **Conclusion:** To fully utilize the **78 dB** dynamic range of the hardware, you must select a window function where the side lobes are effectively below **-78 dB**. This ensures the only noise limiting your detection is the hardware itself, not the windowing mathematics.

> **Source:** Interpretation of spectral masking and side lobes from Chapter 10, Section 10.2.

---

#### 3. Kaiser Window Calculation

We will determine the optimal parameters for a Kaiser window to match the USRP hardware capabilities.

**Given Specifications:**
* **Target Dynamic Range ($A_{sl}$):** 78 dB (To match the hardware dynamic range).
* **Frequency Resolution ($\Delta f$):** 25 kHz ($25,000$ Hz).
* **Sampling Rate ($f_s$):** *Note: The formula requires frequency in radians. As f_s was not specified in this immediate prompt, we will derive the formula in terms of f_s.*

#### Step A: Calculate Beta ($\beta$)
We use the empirical formula for $A_{sl}$ (Side-lobe Attenuation). Since $A_{sl} = 78$ dB, we fall into the range $60 < A_{sl} \le 120$.

**Formula:**
$$\beta = 0.12438(A_{sl} + 6.3)$$

**Calculation:**
1.  Substitute $A_{sl} = 78$:
    $$\beta = 0.12438(78 + 6.3)$$
2.  Add terms:
    $$\beta = 0.12438(84.3)$$
3.  Multiply:
    $$\beta \approx \mathbf{10.485}$$

#### Step B: Calculate Window Length ($L$)
We use the formula relating Length to Attenuation and Main-Lobe Width.

**Formula:**
$$L \approx \frac{24\pi(A_{sl} + 12)}{155 \Delta\omega_{ml}} + 1$$

**Conversions:**
The main-lobe width in radians ($\Delta\omega_{ml}$) is related to the resolution in Hz ($\Delta f$) and sampling rate ($f_s$) by:
$$\Delta\omega_{ml} = \frac{2\pi \Delta f}{f_s}$$

**Substitution:**
1.  Substitute $A_{sl} = 78$ and $\Delta\omega_{ml}$:
    $$L \approx \frac{24\pi(78 + 12)}{155 \cdot (2\pi \cdot 25000 / f_s)} + 1$$
2.  Simplify numerator ($78+12 = 90$):
    $$L \approx \frac{24\pi(90)}{155 \cdot 2\pi \cdot (25000 / f_s)} + 1$$
3.  Cancel $2\pi$ terms:
    $$L \approx \frac{12 \cdot 90}{155 \cdot (25000 / f_s)} + 1$$
    $$L \approx \frac{1080}{155} \cdot \frac{f_s}{25000} + 1$$
4.  Simplify constants ($1080/155 \approx 6.9677$):
    $$L \approx 6.9677 \cdot \frac{f_s}{25000} + 1$$

**Final Result for Length:**
$$L \approx 2.787 \times 10^{-4} \cdot f_s + 1$$

