# Optimized Spectral Analysis of ISM Band Signals via SDR

## Project Description

This project presents a software-defined radio (SDR) framework for high-fidelity signal acquisition and spectral analysis. Utilizing the USRP B210 hardware and a Python-based processing engine, the system implements a dynamic signal conditioning pipeline. Key contributions include an automated Direct Current (DC) offset removal algorithm using a tunable Infinite Impulse Response (IIR) filter and an adaptive Short-Time Fourier Transform (STFT) mechanism. The spectral analysis engine dynamically computes Kaiser window parameters to satisfy strict attenuation ($78$ dB) and resolution ($25$ kHz) requirements, ensuring optimal visualization of Radio Frequency (RF) phenomena such as frequency Hops and Bursts.
## Resources 

| Component | Description | Access File |
| :--- | :--- | :--- |
| **Source Code** | USRP Reciver Code | [View](src/usrp_rx.py) |
| **Results** | Contains results | [View](results/results.md) |
| **Code Documenatation** | Explaination of source code | [View](docs/code_documentation.md) |
| **Mathematical Formulation** | Mathematical formulation and parameters | [View](docs/mathematical_formulation_and_system_parameters.md) |
| **Theory** | Detailed explaination of each Theory realted to project | [View](docs/thoery.md) |
