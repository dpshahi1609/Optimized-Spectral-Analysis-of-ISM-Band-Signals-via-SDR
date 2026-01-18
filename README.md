# Optimized Spectral Analysis of ISM Band Signals via SDR

## Project Description

Efficient signal capturing and spectral analysis play a pivotal role in modern wireless environments, particularly driven by AI/ML applications and Next Generation Networks. This project utilizes USRP hardware and the UHD Python API to facilitate signal acquisition and efficient Short-Time Fourier Transform analysis. Key contributions include an automated Direct Current offset removal using a tunable Infinite Impulse Response filter, alongside an adaptive STFT mechanism. The spectral analysis engine dynamically computes Kaiser window parameters to satisfy strict attenuation and resolution requirements, ensuring optimal visualization of Radio Frequency phenomena such as frequency hops and bursts
## Resources 

| Component | Description | Access File |
| :--- | :--- | :--- |
| **Source Code** | USRP Reciver Code | [View](src/usrp_rx.py) |
| **Results** | Contains results | [View](results/results.md) |
| **Code Documenatation** | Explaination of source code | [View](docs/code_documentation.md) |
