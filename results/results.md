# Optimized Spectral Analysis of ISM Band Signals via SDR

## Project Overview
This project focuses on the capture and analysis of ISM band signals (Bluetooth and Wi-Fi) using Software Defined Radio (SDR). The analysis involves capturing raw I/Q data, performing Short-Time Fourier Transform (STFT), and visualizing the results in both the time domain and frequency domain (spectrograms).

## 1. Bluetooth Signal Analysis
**Center Frequency:** 2.472 GHz | **Bandwidth:** 20.0 MHz

The spectrogram below illustrates the characteristic Frequency Hopping Spread Spectrum (FHSS) behavior of Bluetooth, where the signal rapidly switches carriers to avoid interference.

### Time Domain Response
![Time Domain - 2.472 GHz](images/Figure1.png)
*Figure 1: Decimated time-domain amplitude of the captured signal.*

### Spectrogram (Frequency Domain)
![Spectrogram - 2.472 GHz](images/Figure2.jpg)
*Figure 2: Spectrogram showing distinct frequency hopping bursts typical of Bluetooth communication.*

---

## 2. Wi-Fi Signal Analysis (Channel 6)
**Center Frequency:** 2.437 GHz | **Bandwidth:** 25.0 MHz

The following plots analyze traffic on Wi-Fi Channel 6. Unlike Bluetooth, Wi-Fi signals typically occupy a static bandwidth (Direct Sequence Spread Spectrum or OFDM) and appear as wide blocks of energy in the spectrogram.

### Time Domain Response
![Time Domain - 2.437 GHz Sample 1](images/Figure3.png)
*Figure 3: Time domain amplitude showing bursty packet transmission.*

![Time Domain - 2.437 GHz Sample 2](images/Figure5.png)
*Figure 4: Additional time domain sample of signal bursts.*

### Spectrogram (Frequency Domain)
![Spectrogram - 2.437 GHz Sample 1](images/Figure4.jpg)
*Figure 5: Spectrogram showing wideband energy bursts centered at 2.437 GHz.*

![Spectrogram - 2.437 GHz Sample 2](images/Figure6.jpg)
*Figure 6: Extended spectrogram view of the channel activity.*

---

## Methodology
* **Hardware:** USRP (Universal Software Radio Peripheral)
* **Processing:** Python (NumPy, SciPy)
* **Visualization:** Matplotlib
