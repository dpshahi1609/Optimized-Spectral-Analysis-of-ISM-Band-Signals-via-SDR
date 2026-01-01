# Mathematical Formulation and System Parameters

## I. System Parameters and Configuration

The system operation is governed by the following configuration constants defined in the software.

| Parameter | Symbol | Value / Unit | Description |
| :--- | :---: | :--- | :--- |
| **Window Type** | $w[n]$ | Kaiser | The apodization function used for spectral leakage control. |
| **Target Attenuation** | $A_{sl}$ | $78.0$ dB | Required side-lobe attenuation for the window function. |
| **Target Resolution** | $\Delta f$ | $25.0$ kHz | Desired spectral frequency resolution. |
| **DC Cutoff Frequency** | $f_{c, DC}$ | $25.0$ kHz | The -3dB cutoff frequency for the high-pass DC blocking filter. |
| **Sample Rate** | $f_s$ | Variable (Hz) | The instantaneous sampling rate configured on the USRP B210 hardware. |

## II. Mathematical Formulation

### A. Dynamic DC Blocker (IIR High-Pass Filter)
To mitigate the DC offset inherent in Direct Conversion receivers, a recursive IIR filter is applied. The filter is modeled as a first-order high-pass filter.

**1. Filter Coefficient ($\alpha$):**
The code approximates the pole location $\alpha$ for a given cutoff frequency $f_{c, DC}$ and sampling rate $f_s$ using the small-angle approximation of the exponential function $e^{-x} \approx 1-x$.

$$
\alpha = 1 - \left( \frac{2\pi f_{c, DC}}{f_s} \right)
$$

*Constraint:* The value is clamped to the range $[0.0, 0.999999]$ to ensure stability (pole lies within the unit circle).

**2. Transfer Function:**
The time-domain difference equation implemented is:
$$y[n] = x[n] - x[n-1] + \alpha \cdot y[n-1]$$

This corresponds to the z-domain transfer function:
$$H(z) = \frac{1 - z^{-1}}{1 - \alpha z^{-1}}$$

**3. Transient Settling Time:**
The filter requires a settling period before the output is valid. The time constant $\tau$ (in samples) for the exponential decay is calculated as:

$$
\tau = -\frac{1}{\ln(\alpha)}
$$

The system discards an initial block of samples $N_{discard}$ equivalent to 5 time constants, ensuring the transient response has decayed to negligible levels (approx. 99.3% settled):

$$
N_{discard} = \lceil 5 \tau \rceil
$$

### B. Spectral Analysis (STFT & Kaiser Window)
The system computes the Short-Time Fourier Transform (STFT) using a window designed to meet specific spectral leakage requirements.

**1. Kaiser Window Shape Parameter ($\beta$):**
The shape parameter $\beta$ is derived empirically from the target side-lobe attenuation $A_{sl}$ (in dB). The implementation uses a piecewise function adapted for high-attenuation scenarios:

$$
\beta = 
\begin{cases} 
0.12438 (A_{sl} + 6.3), & \text{if } A_{sl} > 60 \\
0.76609 (A_{sl} - 13.26)^{0.4} + 0.09834 (A_{sl} - 13.26), & \text{if } 13.26 < A_{sl} \le 60 \\
0.0, & \text{if } A_{sl} \le 13.26
\end{cases}
$$

*Note:* $A_{sl} = 78.0$ dB in the default configuration, placing the system in the first case ($>60$).

**2. FFT Length Determination ($N_{FFT}$):**
The required FFT length is calculated dynamically to satisfy the main lobe width requirements imposed by the target resolution $\Delta f$.

First, the normalized angular resolution $\Delta \omega_{ml}$ is defined as:
$$\Delta \omega_{ml} = \frac{2\pi \Delta f}{f_s}$$

The window length $N$ is estimated using the implemented relation:
$$N_{calc} = \frac{24\pi (A_{sl} + 12)}{155 \Delta \omega_{ml}} + 1$$

The final FFT size $N_{FFT}$ is the integer ceiling of $N_{calc}$. If the result is odd, it is incremented by 1 to ensure an even transform length.

**3. Spectrogram Power Calculation:**
The STFT magnitude is converted to a logarithmic scale (dB) for visualization:

$$
P_{dB}[k, m] = 20 \log_{10}(|X[k, m]| + \epsilon)
$$

Where:
* $X[k, m]$ is the DFT of the $m$-th windowed frame.
* $\epsilon = 10^{-12}$ is a small constant added to prevent singularity at zero magnitude.

## III. Acquisition & Hardware Control

The acquisition logic involves a deterministic state machine interfacing with the UHD (USRP Hardware Driver).

1.  **Buffer Sizing:** The target sample count $S_{target}$ is derived strictly from the user-defined dwell time $T_{dwell}$ and bandwidth $BW$:
    $$S_{target} = \lceil T_{dwell} \times BW \rceil$$
2.  **Frequency Tuning:** The LO (Local Oscillator) frequency $f_c$ is set using an integer-N tuning mode request (`mode_n=integer`) to minimize fractional spur noise.

---
*End of Technical Description*
