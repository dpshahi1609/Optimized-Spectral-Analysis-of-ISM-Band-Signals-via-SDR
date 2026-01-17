# Table of Contents
1. [Library Imports and Helper Functions](#[library-imports-and-helper-functions)

--------------------
## Library Imports and Helper Functions

### **1. Imports & Library Usage**

The code imports specific libraries to handle hardware interfacing, numerical computation, and signal filtering.

* `import uhd`:This is the driver library for **USRP** (Universal Software Radio Peripheral) hardware. It is imported to allow the software to interface with SDR hardware for transmitting or receiving radio signals.
* `import numpy as np`: Used for high-performance mathematical operations, specifically array manipulations and mathematical constants (like $\pi$ and logarithms).
* `from scipy.signal import lfilter, get_window`:

  `lfilter`: A function used to filter data using an IIR or FIR filter. It implements the standard difference equation.

  `get_window`: A function used to generate various window shapes (like 'kaiser', 'hamming') which are essential for reducing spectral leakage in signal processing.
* `import matplotlib.pyplot`: It is a collection of functions that provides a MATLAB-like interface for the Matplotlib library in Python. It is the most popular way to generate plots and visualizations in Python.

---

### **2. Parameters & Configuration**

This section defines the constants that control the behavior of the signal processing pipeline.

```python
WINDOW_TYPE = 'kaiser' 
TARGET_ATTENUATION_DB = 78.0
TARGET_RESOLUTION_HZ = 25000.0 

DC_BLOCKER_CUTOFF_HZ = 25000.0 
```

* **`WINDOW_TYPE = 'kaiser'`**: Selects the **Kaiser** window for processing.
* **`TARGET_ATTENUATION_DB = 78.0`**: Sets the desired suppression of noise/side-lobes to **78 decibels**.
* **`DC_BLOCKER_CUTOFF_HZ = 25000.0`**: Defines the **cutoff frequency** for the IIR High Pass filter.

---

### **3. Helper Function: `calculate_optim_alpha`**

This function calculates the feedback coefficient ($\alpha$) for a first-order IIR High-Pass Filter (DC Blocker).

**Code Snippet:**
```python
def calculate_optim_alpha(cutoff_hz, fs):
    if fs <= 0: return 0.99 
    
    alpha = 1.0 - (2.0 * np.pi * cutoff_hz / fs)
    
    return max(0.0, min(0.999999, alpha))
```



**Function Explanation:**
* **Why it is used:** To determine the precise "stiffness" of the filter based on the sampling rate. A fixed alpha would behave differently if the sample rate changed; this function ensures consistent filtering (e.g., always cutting off at 25kHz) regardless of the radio's sample rate.
* **Inputs:**
  * `cutoff_hz` (float): The frequency (in Hz) below which signals should be blocked.
  * `fs` (float): The sampling frequency (in Hz) of the system.
* **Outputs:**
  * `alpha` (float): A value between 0 and 1 (typically very close to 1.0) representing the pole location of the filter.
  

**Logic & Mathematical Explanation:**

1.  **`if fs <= 0: return 0.99`**: 
* **Logic:** A safety check (Guard Clause). A sampling rate of 0 or negative is physically impossible. If this happens due to an error upstream, the function returns a safe, default alpha of `0.99` to prevent division by zero errors.

2.  **`alpha = 1.0 - (2.0 * np.pi * cutoff_hz / fs)`**:

* **Logic:** This line converts the desired cutoff frequency into a discrete pole location.
  
3.  **`return max(0.0, min(0.999999, alpha))`**:This is a "clamping" operation.
* **Why:**
   * If `alpha` $\ge 1.0$, the filter becomes **unstable** (the output will grow to infinity).
   * If `alpha` $< 0$, the filter behaves like a high-frequency toggle rather which is undesired according to our application.
* **Logic:** It forces the result to stay strictly between `0.0` and `0.999999`.

---

### **4. Helper Function: `calculate_settling_samples`**

This function calculates how many initial data samples should be discarded to allow the filter to stabilize.

**Code Snippet:**
```python
def calculate_settling_samples(alpha):
    if alpha >= 1.0 or alpha <= 0.0: return 1000 
    
    tau = -1.0 / np.log(alpha)
    
    n_discard = int(np.ceil(5 * tau))
    
    return n_discard
```



**Function Explanation:**
* **Why it is used:** Recursive (IIR) filters have a "transient response"—a period of time where the output is inaccurate because the internal state is charging up. This function calculates the duration of that period so those bad samples can be thrown away.
* **Inputs:** `alpha` (float): The filter coefficient calculated in the previous function.
* **Outputs:** `n_discard` (int): The number of samples to drop from the beginning of the stream.

**Logic & Mathematical Explanation:**

1.  **`if alpha >= 1.0 or alpha <= 0.0: return 1000`**: Safety check. If `alpha` is invalid (unstable or zero), the math below would fail (log of zero/negative or division by zero). It returns a safe default of 1000 samples.

2.  **`tau = -1.0 / np.log(alpha)`**: Calculates the **Time Constant** ($\tau$) of the filter in samples.

3.  **`n_discard = int(np.ceil(5 * tau))`**: Calculates the total samples to discard based on the "5 Time Constant Rule".

   * **`5 * tau`**: In signal processing theory, a system is considered "fully settled" (99.3% settled) after 5 time constants ($5\tau$).
   * **`np.ceil`**: Rounds the calculated number to the next whole number (you cannot discard a fraction of a sample).
   * **`int(...)`**: Converts the result to an integer so it can be used as an array index.

---
