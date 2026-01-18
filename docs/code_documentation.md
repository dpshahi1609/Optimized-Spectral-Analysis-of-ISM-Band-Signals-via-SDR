# Table of Contents
1. [Library Imports and Helper Functions](#library-imports-and-helper-functions)
2. [USRP Setup](#usrp-setup)
3. [Capture Samples](#capture-samples)
4. [DC Offset Removal](#dc-offset-removal)
5. [IQ Data Visualization](#iq-data-visualization)
6. [STFT Calculation And Visualization](#stft-calculation-and-visualization)
7. [Run Experiment And Main](#run-experiment-and-main)

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

## DC Offset Removal

```python
    def apply_dc_blocker(samples, fs):
        ...
        return filtered[n_discard:]
```
* The function implements a standard First-Order IIR (Infinite Impulse Response) High-Pass Filter. It is designed to remove the 0 Hz component (DC offset) from a digital signal while leaving higher frequencies intact.
* It takes `samples` and `fs` as Inputs.
* Returns `filtered[n_discard:]` as output after discarding unsetteled samples.
---
 ```python
     alpha = calculate_optim_alpha(DC_BLOCKER_CUTOFF_HZ, fs)
     n_discard = calculate_settling_samples(alpha)
```
* `calculate_optim_alpha(DC_BLOCKER_CUTOFF_HZ, fs)` Calculates an Optimal alpha according to given sampling frequency and filter's cutoff frequency.
* `calculate_settling_samples(alpha)` Calculates the no of samples needee to settel filter's response.
---
```python
    if len(samples) < n_discard + 100:
    print("[WARN] Data too short for this filter configuration!")
    return samples
```
* If no of input samples`len(samples)` are shorter than setteling time `n_discard` then filtering it would destroy the entire signal. In this case, it aborts and returns the original data to prevent errors.
---
```python
    b = [1, -1]
    a = [1, -alpha]
    filtered = lfilter(b, a, samples)
    
    return filtered[n_discard:]
```

* `lfilter` Function (from the scipy.signal library) to apply a linear digital filter to a set of data.
* For an input signal $x[n]$ (your samples) and output signal $y[n]$ (your filtered variable), the operation is defined as:
  * $$a[0]y[n] = b[0]x[n] + b[1]x[n-1] + ... + b[M]x[n-M] - a[1]y[n-1] - ... - a[N]y[n-N]$$ Usually, $a[0]$ is set to $1$. If it isn't, lfilter normalizes the coefficients by dividing them by $a[0]$.
* In our case we have $$y[n] = x[n] - x[n-1] + \alpha \cdot y[n-1]$$. So according to above our filter cofficients should be `b = [1, -1]` and `a = [1, -alpha]`.
---
## IQ Data Visualization

### 1. Function Declaration and Parameters

**Code Snippet:**
```python
def plot_time_domain(iq_data, fs, label):
```

* **`iq_data` (Input Parameter):** This is the raw signal data you want to analyze. In Digital Signal Processing (DSP), this is typically a NumPy array of complex numbers (In-phase and Quadrature components). The length of this array determines the duration of the signal shown, and the values determine the height (amplitude) of the wave.
* **`fs` (Input Parameter):** It is required to convert the "sample index" (just a number like 0, 1, 2) into actual "time" (seconds). A higher `fs` means samples are closer together in time.
* **`label` (Input Parameter):** A string text used to name the specific dataset. It appears in the chart title to help the viewer identify which signal is being displayed.

---

### 2. Data Decimation Logic

**Code Snippet:**
```python
    decimation = 100 
    subset = iq_data[::decimation]
```

**Explanation:**
This block reduces the number of points to be plotted. Plotting millions of points is slow and visually indistinguishable on a computer screen.

* **`decimation = 100`:** Defines a factor to reduce the dataset size. It sets a variable to 100, meaning we will only keep 1 out of every 100 samples.
* **`subset = iq_data[::decimation]`:** To create a smaller, manageable array for plotting. This uses Python's list slicing syntax `[start:stop:step]`. By using `::100`, it starts at the beginning, goes to the end, but skips 99 items, picking only every 100th item. If `iq_data` had 1,000,000 points, `subset` will have only 10,000 points.

---

### 3. Time Axis Calculation (Mathematical Logic)

**Code Snippet:**
```python
    t = np.arange(len(subset)) * decimation / fs
```

**Explanation:**
Since we removed data points (decimated), we cannot just assume the time is 0, 1, 2... We must calculate the correct physical time (in seconds) for the remaining points.

* **`np.arange(len(subset))`:** Generates a sequence of integers from 0 up to the number of points in our subset.
   * **Input** `len(subset)` (the count of remaining points).
   * **Outputs:** An array like `[0, 1, 2, ..., N]`.
* **`* decimation`:** Because we skipped points, the "real" index of the $k$-th point in the subset is actually $k \times 100$. This restores the original sample index.
* **`/ fs`:** To convert "sample count" to "seconds", we divide by the sampling rate ($f_s$).
            $$t = \frac{\text{Index} \times \text{Decimation Factor}}{f_s}$$

---

### 4. Setting up the Figure

**Code Snippet:**
```python
    plt.figure(figsize=(10, 3))
```

* **`plt.figure`:** Initializes a new container (window) for the visualization. To ensure this plot does not overlap with previous plots and to define the image dimensions.
* **`figsize=(10, 3)` (Parameter):** Specifies the width and height of the figure in inches. `(10, 3)` creates a wide, short rectangle. This is ideal for time-domain signals because it allows you to see a long duration of time horizontally without wasting vertical space.

---

### 5. Plotting the Waveform

**Code Snippet:**
```python
    plt.plot(t, np.abs(subset), label='Magnitude', color='#004488', linewidth=0.8)
```

* **`np.abs(subset)` (Special Function):** `iq_data` contains complex numbers ($I + jQ$). You cannot plot complex data directly on a 2D Y-axis w.r.t to time. We need the "Magnitude".
   * **Logic:** It calculates the Euclidean distance from the origin: $\text{Magnitude} = \sqrt{I^2 + Q^2}$.
   * **Input:** Array of complex numbers.
   * **Output:** Array of real, positive floating-point numbers.
* **`plt.plot` Function:** draws lines connecting the data points.
   * **`t` (Input):** The X-axis coordinates (Time).
   * **`np.abs(subset)` (Input):** The Y-axis coordinates (Amplitude).
   * **`color='#004488'` (Parameter):** Uses a specific Hex code for a dark blue color. This affects the aesthetics, making it look professional.
   * **`linewidth=0.8` (Parameter):** Sets the thickness of the line. A thinner line (0.8) is used here to make the signal look crisp rather than "blobby," especially with dense data.

---

### 6. Labels and Formatting

**Code Snippet:**
```python
    plt.title(f"Time Domain (Decimated) - {label}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
```

* **`plt.title(...)`:** Uses an f-string to insert the `label` variable dynamically into the title text. Provides context to the viewer about what the graph represents.
* **`plt.xlabel` / `plt.ylabel`:** Labels the axes with units (Seconds for X, Amplitude for Y) so the data is scientifically meaningful.
* **`plt.grid(True, alpha=0.3)`:** Draws a grid behind the plot to make it easier to estimate values visually.
   * **`alpha=0.3` (Parameter):** Sets the transparency. `0.3` means 30% opaque. This ensures the grid is visible but faint enough not to distract from the main signal line.
* **`plt.tight_layout()`:** An automatic adjustment function that fixes padding. Prevents axis labels or titles from being cut off by the edge of the image.
* **`plt.show()`:** The command to actually render and display the window to the user.
---
## STFT Calculation And Visualization

### 1. Function Overview & Inputs

This function performs a **Short-Time Fourier Transform (STFT)** manually to analyze the frequency content of a signal over time and visualizes the result as a spectrogram.

**Code Snippet:**
```python
def compute_and_plot_block_stft(data, fs, fc, label):
    print("[INFO] Computing STFT...")
```

**Function Parameters:**
* `data` (**Input Array**): The raw signal data (likely complex I/Q samples) to be analyzed.
* `fs` (**Float**): The **Sampling Frequency** in Hz.
* `fc` (**Float**): The **Center Frequency** in Hz.
* `label` (**String**): A text label used in the plot title to identify the signal.

---

### 2. Kaiser Window Parameter ($\beta$) Calculation

This section calculates the $\beta$ (beta) parameter required for generating a **Kaiser Window**. The Kaiser window is a mathematical function used to reduce "spectral leakage" (noise bleeding into adjacent frequencies) during the Fourier Transform.



**Code Snippet:**
```python
    Asl = TARGET_ATTENUATION_DB
    
    if Asl > 60:
        beta_val = 0.12438 * (Asl + 6.3)
    elif Asl > 13.26:
        beta_val = 0.76609 * (Asl - 13.26)**0.4 + 0.09834 * (Asl - 13.26)
    else:
        beta_val = 0.0
```

**Logic Explanation:**
* `Asl = TARGET_ATTENUATION_DB`: This variable sets the desired side-lobe attenuation in decibels (dB). This implements the standard empirical piecewise formula for the Kaiser window $\beta$ parameter based on the desired attenuation ($A$):


---

### 3. Window Length Calculation (`n_fft`)

This block calculates the optimal size of the FFT (Fast Fourier Transform) window to achieve a specific frequency resolution.

**Code Snippet:**
```python
    delta_ml = 2 * np.pi * (TARGET_RESOLUTION_HZ / fs)
    numerator = 24 * np.pi * (Asl + 12)
    denominator = 155 * delta_ml
    n_fft_calc = (numerator / denominator) + 1
    n_fft = int(np.ceil(n_fft_calc))
    if n_fft % 2 != 0: n_fft += 1
```

**Logic Explanation:**
* Calculates the optimal size of the FFT (Fast Fourier Transform) window to achieve a specific frequency resolution according to $$N_{calc} = \frac{24\pi (A_{sl} + 12)}{155 \cdot 2\pi \frac{\Delta f}{f_s}} + 1$$
* `delta_ml`: Calculates the normalized transition width in radians. It converts the user's desired resolution (`TARGET_RESOLUTION_HZ`) relative to the sample rate `fs`.
* `numerator` / `denominator`: These lines implement the Kaiser filter order estimation formula. It estimates how many samples (`n_fft`) are needed to achieve the target resolution and attenuation.
* `n_fft = int(np.ceil(n_fft_calc))`: The result is rounded up to the nearest integer because array sizes must be whole numbers.
* `if n_fft % 2 != 0`: This ensures `n_fft` is an **even number**.
  * `**Why?**` Many FFT algorithms operate more efficiently on even numbers, and it simplifies calculating center points and overlaps.

---

### 4. Window Generation and Buffer Setup

Here, the code creates the window object and prepares the empty matrix (buffer) that will hold the final spectrogram image.

**Code Snippet:**
```python
    hop_length = n_fft // 2
    window = np.kaiser(n_fft, beta=beta_val)

    n_samples = len(data)
    n_frames = (n_samples - n_fft) // hop_length + 1
    
    if n_frames <= 0:
        print("[ERROR] Data too short for analysis.")
        return

    spectrogram_data = np.zeros((n_fft, n_frames), dtype=np.float32)
```

**Special Functions & Objects:**
* `hop_length = n_fft // 2`: This defines a **50% overlap**. The window slides forward by half its length each step. Overlapping ensures we don't lose data at the edges of the window where the signal is tapered to zero.
* `np.kaiser(n_fft, beta=beta_val)`:
  * **Why used:** To generate the window coefficients.
  * **Inputs:** Length of the window (`n_fft`) and the shape parameter (`beta`).
  * **Output:** An array of shape `(n_fft,)` containing numbers between 0 and 1. This will be multiplied by the signal to taper the edges to zero.
* `len(data)`: Simply counts the total number of data points (samples) in your input signal array data.
*  `n_frames`: Calculates mathematically how many "steps" fit into the total data length `n_samples`.
*  `if n_frames <= 0:`: f your input `data` is shorter than a single window size (n_fft), you cannot perform even one Fourier Transform. n_frames would be zero or negative, so the code stops to prevent a crash later.
* `np.zeros(...)`: Initializes a matrix of zeros.
   * **Why used:** Pre-allocating memory is faster than growing a list inside a loop.
   * **Inputs:** Shape `(rows, columns)` and data type. Here, rows are frequency bins (`n_fft`) and columns are time steps (`n_frames`).

---

### 5. The STFT Processing Loop

This is the core engine of the function. It processes the signal one "chunk" at a time.



**Code Snippet:**
```python
    for i in range(n_frames):
        start = i * hop_length
        end = start + n_fft
        chunk = data[start:end]
        windowed = chunk * window
        fft_res = np.fft.fft(windowed)
        fft_shifted = np.fft.fftshift(fft_res)
        mag_db = 20 * np.log10(np.abs(fft_shifted) + 1e-12)
        spectrogram_data[:, i] = mag_db
```

**Logic Explanation (Line by Line):**

* `start` / `end`: Calculates the indices to slice the current segment of data.
* `chunk = data[start:end]`: Extracts the raw signal for this specific time slice.
* `windowed = chunk * window`: Applies the Kaiser window.
    * **How it works:** Element-wise multiplication. This smooths the signal at the boundaries to prevent spectral artifacts.
* `fft_res = np.fft.fft(windowed)`: Converts the signal from Time Domain (amplitude vs time) to Frequency Domain (amplitude vs frequency).
   * **Input:** Time-series array.
   * **Output:** Array of Complex numbers representing frequency components.
* `fft_shifted = np.fft.fftshift(fft_res)`: Standard FFT outputs frequencies in the order [0...Pos...Neg]. `fftshift` rearranges them to [-Neg...0...Pos], placing 0Hz (DC) in the center.
* `mag_db = 20 * np.log10(...)`: Converts magnitude to the **Decibel (dB)** scale.
   * `np.abs(fft_shifted)`: Calculates magnitude of the complex numbers ($\sqrt{real^2 + imag^2}$).
   * `+ 1e-12`: Adds a tiny number (epsilon) to prevent a "Divide by Zero" error if the magnitude is exactly 0 (since $\log(0)$ is undefined).
   * `20 * ...`: Standard scaling factor for field quantities (like voltage) to dB.
* `spectrogram_data[:, i] = mag_db`: Stores the result in the pre-allocated matrix. The `:` indicates all frequency rows, `i` is the current time column.

---

### 6. Visualization (Plotting)

This section renders the calculated data as a heatmap.

**Code Snippet:**
```python
    duration = n_samples / fs
    freq_min = (fc - fs/2) / 1e6
    freq_max = (fc + fs/2) / 1e6
    
    plt.figure(figsize=(12, 6))
    plt.imshow(spectrogram_data, 
               aspect='auto', 
               origin='lower', 
               extent=[0, duration, freq_min, freq_max],
               cmap='inferno',
               interpolation='nearest')

    plt.colorbar(label='Power (dB)')
    plt.title(f"Spectrogram | {label}\nRes: {TARGET_RESOLUTION_HZ/1000} kHz | Cutoff: {DC_BLOCKER_CUTOFF_HZ/1000} kHz") 
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (MHz)")
    plt.tight_layout()
    plt.show()
```

* `n_samples / fs`: Calculates the total length of the Signal in seconds.
* `freq_min` / `freq_max`: Calculates the physical frequency range for the Y-axis. It centers the view around `fc` (Center Frequency) and spans half the sample rate (`fs/2`) in both directions. Division by `1e6` converts Hz to MHz.
* `plt.figure(figsize=(12, 6))`: Creates the drawing canvas. Sets the size to 12 inches wide by 6 inches tall.
* `plt.imshow`: This is the core command that draws the 2D array (spectrogram_data) as an image. The arguments control how that data is interpreted.
   * `aspect='auto'`: By default, imshow tries to keep pixels square. Since spectrograms usually have many more time steps than frequency bins (or vice versa), forcing square pixels would squash the plot into a thin line. auto allows the aspect ratio to stretch to fill the figure area.
   * `origin='lower'`: By default, image arrays start at the top-left (like a photograph). In science, the Y-axis (Frequency) should start at the bottom (low frequency) and go up. This flips the vertical axis so low frequencies are at the bottom.
   * `extent=[0, duration, freq_min, freq_max]`: his maps the abstract array pixels to the real-world units calculated in Part 1. **Format:** `[x_min, x_max, y_min, y_max]`. It tells the plot: "The left edge is 0 seconds, the right edge is duration seconds, the bottom edge is freq_min, and the top edge is freq_max."
   * `cmap='inferno'`: Sets the color map. inferno is a perceptually uniform colormap that goes from black (low power) to red/yellow (high power). It is excellent for dark backgrounds and printing.
   * `interpolation='nearest'`: nearest means "don't blur." It renders sharp pixels. This is preferred for scientific data so you see the raw resolution rather than a smoothed, potentially misleading image.
* `plt.colorbar(label='Power (dB)')`: Adds the color legend on the side showing which color corresponds to which decibel (dB) level.

---
Here is the documentation for your USRP (Universal Software Radio Peripheral) project code. This code is designed to capture radio frequency signals and perform signal processing tasks like time-domain plotting and Short-Time Fourier Transform (STFT) analysis.

---
## Run Experiment And Main

### **Part 1: Run Experiment Function**

The function `run_experiment` is the core logic that configures the hardware for a specific test case, captures data, and triggers analysis.

### **1. Function Definition & Logging**

```python
def run_experiment(usrp, fc, bw, dwell, label):
    print(f"\n[TASK] Starting Run: {label}")
```

* **`def run_experiment(...)`**: To encapsulate a single "run" of data capture and analysis so it can be repeated with different settings.
   * **Inputs:**
      * `usrp`: The initialized USRP device object (controls the hardware).
      * `fc`: Center Frequency in Hz (float).
      * `bw`: Bandwidth in Hz (float).
      * `dwell`: Time in seconds to record (float).
      * `label`: A string used to name plots or logs (e.g., "2.4GHz_BW20M").
   * **Output:** it performs actions and plots data.

---

### **2. Configuring the USRP Hardware**

```python
    usrp.set_rx_rate(bw, 0)
    usrp.set_rx_freq(uhd.types.TuneRequest(fc), 0)
    usrp.set_rx_bandwidth(bw, 0)
```

* This section configures the radio hardware. These methods are part of the UHD (USRP Hardware Driver) API.

---

### **3. Stabilization & Capture**

```python
    time.sleep(1.0) 
    
    iq_data = capture_samples(usrp, dwell, bw)
```

* `time.sleep(1.0)`: Hardware tuning (PLL locking) takes time. If you capture immediately after setting the frequency, the signal might be unstable or garbage. Pauses execution for 1 second.
* `capture_samples(usrp, dwell, bw)`: This is a helper function (Already defined) that streams raw IQ data from the USRP to the computer's memory.

---

### **4. Validation & Processing Logic**

```python
    if len(iq_data) > 2000:
        iq_clean = apply_dc_blocker(iq_data, fs=bw)
        
        plot_time_domain(iq_clean, bw, label)
        compute_and_plot_block_stft(iq_clean, bw, fc, label)
    else:
        print("[ERROR] Not enough data captured.")
```

* `if len(iq_data) > 2000:` Ensures we actually received valid data. If the buffer is empty or too small, processing it would crash the programe.
* `iq_clean = apply_dc_blocker(iq_data, fs=bw)` / `plot_time_domain(iq_clean, bw, label)` / `compute_and_plot_block_stft(iq_clean, bw, fc, label)`: these are some predefined helper functions which are now used for a single run.
---

## **Part 2: The Main Execution Block**

This section handles the user interface, input validation, and the main program loop.

### **1. Entry Point & Setup**

```python
if __name__ == "__main__":
    try:
        usrp_dev = setup_usrp(2440e6, 20e6, 30)
```

* `if __name__ == "__main__":` Standard Python practice. It ensures this code runs only if the file is executed directly, not if it's imported as a module.
* `setup_usrp(2440e6, 20e6, 30)` Initializes the connection to the USRP device before we start the loop. The values 2440e6 and 20e6 in that line are dummy values. They are used solely to get the device into a "Ready" state. They will be immediately overwritten by whatever you type into the input() prompt before any actual data is recorded.

---

### **2. User Interface Loop**

```python
        while True:
            print("\n--- NEW EXPERIMENT ---")
            try:
                raw_fc = float(input("Enter Center Freq (GHz) [0 to Exit]: "))
                if raw_fc == 0: break
                
                raw_bw = float(input("Enter Bandwidth (MHz) [Default 20]: ") or 20)
                dwell = float(input("Enter Dwell Time (s) [Default 1.0]: ") or 1.0)
            
            except ValueError:
                print("Invalid Input. Please enter numbers.")
                continue
```

* `while True:` Creates an infinite loop so the user can run multiple experiments without restarting the script. `input` pauses the program and waits for the user to type. `float` tries to convert that text to a number.
* `if raw_fc == 0: break` Provides a clean way to exit the infinite loop.
* `or 20` inside `float(...)` Handles default values. If the user just hits "Enter" (empty string), Python evaluates `"" or 20`, resulting in 20.
* `try... except ValueError:` Prevents the program from crashing if the user types "abc" instead of a number. If conversion fails, it prints an error and uses `continue` to jump back to the start of the `while` loop.

---

### **3. Unit Conversion & Execution**

```python
            fc = raw_fc * 1e9
            bw = raw_bw * 1e6
            label = f"{raw_fc}GHz_BW{raw_bw}M"
            
            run_experiment(usrp_dev, fc, bw, dwell, label)
```

* `fc = raw_fc * 1e9` / `bw = raw_bw * 1e6` Unit Conversion
* `run_experiment(...)` Passes the newly calculated parameters and the existing USRP device to the experiment logic explained in Part 1.

---

### **4. Global Error Handling**

```python
    except KeyboardInterrupt:
        print("\n[INFO] User stopped the script.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
```

* `except KeyboardInterrupt:` Handles the `Ctrl+C` command gracefully. Instead of showing a messy "Traceback" error, it prints a polite exit message.
* `except Exception as e:` Catch-all for unexpected hardware errors (e.g., USRP unplugged). `e` is the exception object containing the error details. Prints the critical error message so the user knows what went wrong.
