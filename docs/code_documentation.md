# Table of Contents
1. [Library Imports and Helper Functions](#[library-imports-and-helper-functions)
2. [USRP Setup](#usrp-setup)

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
* **Outputs:** `alpha` (float): A value between 0 and 1 (typically very close to 1.0) representing the pole location of the filter.
  

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

## USRP Setup

### 1. Function Definition and Inputs

**Code Snippet:**
```python
def setup_usrp(fc, fs, gain):
    ...
    return usrp
```

* **Why it is used:** To create a reusable block of code that allows you to easily change radio settings without rewriting the connection logic every time.
* **Parameters (Inputs):**
  * `fc` (float): **Center Frequency**. This controls the specific radio frequency the device will listen to (e.g., 915 MHz or 2.4 GHz).
  * `fs` (float): **Sampling Rate**. This determines how many samples per second the device captures.
  * `gain` (float): **Receive Gain**. This controls the amplification of the incoming analog signal (in dB).
* **Outputs:** `return usrp`:
  * **Why it is used:** Passes the configured `usrp` object back to the code that called this function.
  * **Output:** The initialized and ready-to-use device object.

---

### 2. Device Connection and Error Handling

**Code Snippet:**
```python
    print(f"[INFO] Connecting to USRP B210...")
    try:
        usrp = uhd.usrp.MultiUSRP("type=b200")
        usrp.set_clock_source("internal")
    except RuntimeError as e:
        print(f"[CRITICAL] USRP Connection Failed: {e}")
        print("Make sure the device is plugged in and recognized by 'uhd_find_devices'.")
        raise
```

* `try: ... except RuntimeError as e:` Hardware initialization is prone to errors (e.g., device not plugged in, USB permission issues). This block attempts to run the code in the `try` section. If a specific error (`RuntimeError`) occurs, it jumps to the `except` block to handle it gracefully instead of crashing instantly with a cryptic message.
* `usrp = uhd.usrp.MultiUSRP("type=b200")`:This is the primary class in the UHD library used to control USRP devices. This instructs the driver to look specifically for a B200-series device. If you have multiple B200s connected, this will pick the first one found. You can be more specific by adding a serial number: `"type=b200, serial=123456"`
  * **Output:** The Python object usrp is created. This object is now your "handle" to the hardware. You will use usrp for all subsequent commands (setting frequency, gain, etc.).
* `usrp.set_clock_source("internal")`: Sets the timing reference for the device. The B210 needs a clock to drive its oscillators. String `"internal"` (uses the device's built-in oscillator) or `"external"` (uses a cable connected to the 10MHz port).
* `raise`: If the connection failed, the program cannot continue. This command re-triggers the error to stop the program after printing the helpful error message.

---

### 3. Advanced Tuning Configuration

**Code Snippet:**
```python
    tune_req = uhd.types.TuneRequest(fc)
    tune_req.args = uhd.types.DeviceAddr("mode_n=integer") 
```

* `uhd.types.TuneRequest(fc)`: This creates a TuneRequest object for a target frequency fc (e.g., $2.4 \text{ GHz}$).Normally, you might just pass the frequency as a float to set_center_freq, but creating a TuneRequest object allows you to pass advanced configuration options (like LO offsets or synthesis modes).

* `uhd.types.DeviceAddr("mode_n=integer")`: This specific argument configures the synthesizer mode. By setting `mode_n=integer`, you force the hardware to use Integer-N mode generally provides better phase noise performance (cleaner signal) compared to Fractional-N mode, but it limits the tuning steps to integer multiples of the reference frequency. This is often preferred for high-quality signal reception.

---

### 4. Applying Radio Settings

**Code Snippet:**
```python
    usrp.set_rx_rate(fs, 0)
    usrp.set_rx_freq(tune_req, 0)
    usrp.set_rx_gain(gain, 0)
    usrp.set_rx_bandwidth(fs, 0)
```

All functions here share a common parameter format: `(Value, Channel Index)`.
* **The Channel Parameter (`0`):** The USRP B210 has two receive channels (RX1 and RX2). The `0` specifies that these settings should apply to the (RX1). If you wanted to configure the second port, you would use `1`.

**Detailed Breakdown:**
* `usrp.set_rx_rate(fs, 0)`: Sets the sample rate of the Analog-to-Digital Converter (ADC) decimation chain. To define the speed at which data is sent from the USRP to the host computer.
* `usrp.set_rx_freq(tune_req, 0)`: Tunes the radio frequency frontend. Instead of passing a simple float, we pass the `tune_req` object we created earlier to apply the "Integer-N" optimization.
* `usrp.set_rx_gain(gain, 0)`: Sets the RF amplifier gain. To adjust signal amplitude.
* `usrp.set_rx_bandwidth(fs, 0)`: Configures the analog low-pass filter on the device. This filters out noise and signals outside your interest *before* digitization. Setting this equal to `fs` (sample rate) is a standard practice to prevent aliasing, ensuring you only receive the bandwidth you can actually capture.

---

### 5. Stabilization and Return

**Code Snippet:**
```python
    time.sleep(1.0)
    return usrp
```

**Explanation of Logic:**
* `time.sleep(1.0)`: Pauses the program execution for 1 second. When hardware parameters (especially the Local Oscillator frequency and analog filters) are changed, they take a small amount of time to "settle" or stabilize. Reading data immediately after tuning can result in garbage data or DC offsets. This delay ensures the hardware is stable before the main program starts reading data.

---
