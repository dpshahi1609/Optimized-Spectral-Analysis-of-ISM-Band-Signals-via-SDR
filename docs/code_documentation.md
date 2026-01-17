# Table of Contents
1. [Library Imports and Helper Functions](#library-imports-and-helper-functions)
2. [USRP Setup](#usrp-setup)
3. [Capture Samples](#capture-samples)

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

## Capture Samples

### **1. Function Definition and Target Calculation**

This section defines the function and calculates exactly how many data points we need to collect based on the requested time duration.

```python
def capture_samples(usrp_dev, duration, fs):
    num_samps_target = int(np.ceil(duration * fs))
```

#### **Parameters Explained**
* **`usrp_dev`**: This is the handle object representing the physical USRP hardware. It allows the code to send commands to the specific radio connected to the computer.
* **`duration`**: Defines how long (in seconds) the capture should last.
* **`fs`**: Stands for "Sampling Frequency" (samples per second).

#### **Logic Explanation**
* **`duration * fs`**: This is a mathematical conversion from *Time domain* to *Sample domain*.
   * *Example:* If you want 0.5 seconds of data (`duration`) at a rate of 1,000 samples/sec (`fs`), you need $0.5 \times 1000 = 500$ total samples.
* **`np.ceil(...)`**: You cannot capture a fraction of a sample. If the math results in 500.2 samples, `ceil` (ceiling) rounds it up to 501 to ensure we cover the full duration.
* **`int(...)`**: Hardware drivers require integer counts (whole numbers), not decimals.

---

### **2. Stream Configuration**

Here, we tell the USRP how to format the data before sending it to the computer.

```python
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    streamer = usrp_dev.get_rx_stream(st_args)
```

#### **Special Objects Explained**
* **`uhd.usrp.StreamArgs("fc32", "sc16")`**: This object tells the UHD driver how to format the data when moving it between the radio hardware and your computer's CPU.
   * **Input 1 ("fc32"):** "Float Complex 32-bit". This tells the driver that your Python application wants to handle the data as complex numbers where the real and imaginary parts are 32-bit floating-point numbers.
   * **Input 2 ("sc16"):** "Signed Complex 16-bit". This tells the USRP to send data over the cable (Ethernet or USB) as 16-bit signed integers. It halves the bandwidth required compared to sending 32-bit floats over the wire. The driver automatically converts these 16-bit integers into the "fc32" floats you requested for the CPU.
* **`usrp_dev.get_rx_stream(st_args)`**: usrp_dev is assumed to be an instantiated `MultiUSRP` object (the connection to your physical radio). `get_rx_stream(st_args)` creates the actual RX Streamer object based on the arguments you defined above. You will use this `streamer` object later to issue streaming commands (like `stream_cmd`) and to actually receive the samples `using streamer.recv()`.

---

### **3. Buffer and Metadata Initialization**

We need to prepare memory to catch the incoming data.

```python
    max_samps = streamer.get_max_num_samps()
    recv_buffer = np.zeros((1, max_samps), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()
```

#### **Code Logic Explained**
* **`streamer.get_max_num_samps()`**: The hardware transfers data in "packets" (chunks). This function queries the driver for the maximum number of samples that can fit in a single packet. Ensures our buffer is large enough to hold the largest possible incoming chunk.
* **`np.zeros((1, max_samps), dtype=np.complex64)`** Pre-allocates a "bucket" (`recv_buffer`) to temporarily hold one chunk of incoming data.
   * **Parameter `(1, max_samps)`:** Creates a 2D array (1 channel x max samples).
   * **Parameter `dtype=np.complex64`:** Matches the "fc32" setting defined earlier.
* **`uhd.types.RXMetadata()`**: Creates a container to hold information *about* the received data (e.g., timestamps, error codes) rather than the data itself.

---

### **4. Issuing the Stream Command**

We command the hardware to start sending data.

```python
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
    stream_cmd.num_samps = num_samps_target
    stream_cmd.stream_now = True
    stream_cmd.time_spec = usrp_dev.get_time_now()

    print(f"[INFO] Capturing {duration}s ({num_samps_target} samples)...")
    streamer.issue_stream_cmd(stream_cmd)
```

* **`uhd.types.StreamCMD`**: This creates a command object. The key argument is StreamMode.num_done. This tells the USRP's FPGA: "I want you to send a specific number of samples and then stop automatically.". The other common mode is start_cont (Start Continuous), which streams indefinitely until told to stop.
* **`stream_cmd.num_samps`**: This sets the exact integer number of samples the FPGA should send before halting. This corresponds strictly to the num_done mode set in the previous line. 
* **`stream_cmd.stream_now = True`**: This instructs the USRP to execute this command as soon as it is received and processed by the FPGA, without waiting for a specific timestamp.
* **`stream_cmd.time_spec = usrp_dev.get_time_now()`**:This sets a time for the command to execute.
* **`streamer.issue_stream_cmd(stream_cmd)`**: This sends the configuration object over the transport (USB/Ethernet) to the radio hardware. Once the radio receives this, it will begin pushing data into the network buffer.
* **Complete Block Logic**: The USRP turns on, sends exactly (`num_samps`) samples, and then automatically turns off (stops streaming). 
---

### **5. The Reception Loop (Core Logic)**

Since the USRP sends data in small chunks (e.g., 2,000 samples at a time) but we might want 1,000,000 samples, we must use a loop to collect them all.

```python
    full_data = np.zeros(num_samps_target, dtype=np.complex64)
    samps_received = 0
    timeout_counter = 0

    while samps_received < num_samps_target:
        samps = streamer.recv(recv_buffer, metadata)
```

* **`full_data = np.zeros(...)`**: This is the "final destination" array large enough to hold the entire capture.
* **`while samps_received < num_samps_target:`**: This loop continues to run as long as we haven't collected the total required samples.
* **`streamer.recv(recv_buffer, metadata)`**: Tries to pull one packet of data from the driver into our temporary `recv_buffer`. The buffer to fill and the metadata object to update. (`samps`) Returns an integer representing how many samples were *actually* received in this specific chunk.

---

### **6. Error Handling in the Loop**

We must check if the hardware reported any issues with the chunk we just received.

```python
        if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
            print(f"[ERROR] {metadata.strerror()}")
            if metadata.error_code != uhd.types.RXMetadataErrorCode.overflow:
                break
```

* **`metadata.error_code != ...none`**: Checks if the transaction was not successful.
* **`overflow`**: This specific error means the computer was too slow to process the data, and the USRP internal buffer filled up and dropped data. The code prints an error but decides (via the `if` logic) whether to stop or continue.
* **`break`**: If the error is not an overflow (e.g., a timeout or hardware failure), the loop is immediately terminated to prevent freezing.

---

### **7. Storing the Data**

If data was received, copy it from the temporary buffer to the main array.

```python
        if samps > 0:
            end_idx = min(samps_received + samps, num_samps_target)
            count = end_idx - samps_received
            full_data[samps_received:end_idx] = recv_buffer[0, :count]
            samps_received += count
            timeout_counter = 0
```

* **`end_idx = min(...)`**: Safety logic. If the USRP sends slightly more data than requested (rare but possible), `samps_received + samps` might exceed the size of `full_data`, causing a crash. `min` ensures we never calculate an index beyond the array size.
* **`count = end_idx - samps_received`**: Calculates exactly how many samples from the current chunk fit into the remaining space of `full_data`.
* **`full_data[samps_received:end_idx] = recv_buffer[0, :count]`**: Copies only the valid samples (`:count`) from the temp buffer into the correct position (`samps_received` to `end_idx`) in the main array.
* **`samps_received += count`**: Updates our progress counter.

---

### **8. Handling Timeouts**

If no data arrives, we increment a counter to avoid waiting forever.

```python
        else:
            timeout_counter += 1
            if timeout_counter > 1000:
                print("[WARN] Timeout waiting for samples.")
                break

    print(f"[INFO] Capture Complete. Acquired {len(full_data)} samples.")
    return full_data
```

* The `else` block executes specifically when `streamer.recv()` returns `0`, indicating no samples were received during that specific iteration.
* The `timeout_counter` tracks consecutive "empty" reads. It resets to 0 whenever data is successfully received (in the `if` block above).
* If the counter exceeds the threshold (1000 iterations), the loop is forcibly broken. This prevents the application from freezing on a lost connection.
* Once the loop concludes (either via target reached or timeout), the function reports the total captured size and returns the NumPy array.

---

