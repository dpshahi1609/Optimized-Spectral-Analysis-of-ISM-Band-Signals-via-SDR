
# Code Explaination

This document provides a detailed, line-by-line breakdown of the provided Python code, which is designed to interface with a USRP B210 software-defined radio, capture signals, process them to remove DC offset, and visualize the results using time-domain plots and Short-Time Fourier Transforms (STFT).

## 1. Imports and Library Setup

The code begins by importing the necessary external libraries.

```python
import uhd
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.signal import lfilter, get_window
```

* **`import uhd`**: Imports the **Universal Hardware Driver (UHD)** wrapper for Python. This library allows Python to communicate with Ettus Research USRP (Universal Software Radio Peripheral) hardware. It handles the low-level USB or Ethernet communication, allowing us to tune frequencies, set sample rates, and stream data.
* **`import numpy as np`**: Imports **NumPy**, the fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices (like signal data), along with a collection of mathematical functions to operate on these arrays efficiently. We alias it as `np` for brevity.
* **`import matplotlib.pyplot as plt`**: Imports the `pyplot` module from **Matplotlib**, a plotting library. `pyplot` provides a MATLAB-like interface for creating static, animated, and interactive visualizations (graphs, spectrograms). We alias it as `plt`.
* **`import time`**: Imports Python's built-in **time** module, which provides various time-related functions. In this script, it is primarily used to introduce delays (pauses) to allow hardware to settle.
* **`from scipy.signal import lfilter, get_window`**: Imports specific functions from the `scipy.signal` module (part of the SciPy ecosystem for mathematics and engineering).
    * `lfilter`: A function used to filter data using an IIR (Infinite Impulse Response) or FIR (Finite Impulse Response) filter defined by numerator (`b`) and denominator (`a`) coefficients.
    * `get_window`: A function to generate window functions (like Kaiser, Hamming, etc.), which are crucial in spectral analysis to reduce spectral leakage.

---

## 2. Parameters & Configuration

This section defines global constants that control the behavior of the signal processing and hardware.

```python
WINDOW_TYPE = 'kaiser' 
TARGET_ATTENUATION_DB = 78.0
TARGET_RESOLUTION_HZ = 25000.0 

DC_BLOCKER_CUTOFF_HZ = 25000.0 
```

* **`WINDOW_TYPE = 'kaiser'`**: Sets the type of window function to use for the STFT later. The Kaiser window is chosen because it allows for adjustable side-lobe attenuation, making it versatile for detecting weak signals near strong ones.
* **`TARGET_ATTENUATION_DB = 78.0`**: Defines the desired side-lobe attenuation for the window function in decibels (dB). This value influences the `beta` parameter of the Kaiser window. Higher attenuation reduces "leakage" from strong signals but widens the main signal peak.
* **`TARGET_RESOLUTION_HZ = 25000.0`**: Specifies the desired frequency resolution in Hertz. This determines how close two frequency peaks can be while still being distinguishable. This value is used to calculate the necessary FFT size (`n_fft`).
* **`DC_BLOCKER_CUTOFF_HZ = 25000.0`**: Defines the cutoff frequency for the DC blocker filter. Frequencies below 25 kHz will be attenuated. This is used to remove the "DC offset" (a spike at 0 Hz common in SDRs) without affecting the signal of interest.

---

## 3. Helper: Dynamic Filter Calculations

These functions calculate the mathematical parameters required for the DC blocker filter based on the sampling rate (`fs`) and the cutoff frequency.

### Function: `calculate_optim_alpha`

```python
def calculate_optim_alpha(cutoff_hz, fs):
    if fs <= 0: return 0.99 
    
    alpha = 1.0 - (2.0 * np.pi * cutoff_hz / fs)
    
    return max(0.0, min(0.999999, alpha))
```

* **`def calculate_optim_alpha(cutoff_hz, fs):`**: Defines a function named `calculate_optim_alpha` taking `cutoff_hz` (target filter cutoff) and `fs` (sampling rate) as inputs.
* **`if fs <= 0: return 0.99`**: A safety check. If the sampling rate is zero or negative (invalid), it returns a default safe value of 0.99 to prevent division by zero errors.
* **`alpha = 1.0 - (2.0 * np.pi * cutoff_hz / fs)`**: This calculates the filter coefficient $\alpha$ (alpha) for a single-pole IIR high-pass filter.
    * The formula derives from the relationship between the time constant and cutoff frequency in discrete time.
    * Ideally, $\alpha \approx e^{-2\pi f_c / f_s}$. For small $f_c/f_s$ ratios (common in DC blocking), the approximation $1 - x \approx e^{-x}$ is used.
    * A higher $\alpha$ (closer to 1) results in a narrower notch at DC (lower cutoff frequency).
* **`return max(0.0, min(0.999999, alpha))`**: Clamps the result to ensure $0 \le \alpha < 1$.
    * `min(0.999999, alpha)`: Ensures alpha never actually reaches 1.0 (which would block everything or cause instability).
    * `max(0.0, ...)`: Ensures alpha is never negative.

### Function: `calculate_settling_samples`

```python
def calculate_settling_samples(alpha):
    if alpha >= 1.0 or alpha <= 0.0: return 1000 
    
    tau = -1.0 / np.log(alpha)
    
    n_discard = int(np.ceil(5 * tau))
    
    return n_discard
```

* **`def calculate_settling_samples(alpha):`**: Defines a function to determine how many samples to throw away at the start of filtering. IIR filters have a "transient response" where the output is incorrect while the filter's internal state settles.
* **`if alpha >= 1.0 or alpha <= 0.0: return 1000`**: Validates `alpha`. If it's invalid, returns a safe default of 1000 samples.
* **`tau = -1.0 / np.log(alpha)`**: Calculates the time constant ($\tau$) of the filter in samples.
    * The time constant represents how long it takes for the transient to decay by factor $1/e$ (approx 36.8%).
    * Since $\alpha$ is typically close to 1, `np.log(alpha)` is a small negative number.
* **`n_discard = int(np.ceil(5 * tau))`**: Calculates the number of samples to discard.
    * Engineering rule of thumb: A system is considered "settled" (transient decayed to < 1%) after 5 time constants ($5\tau$).
    * `np.ceil`: Rounds up to the nearest integer to be safe.
* **`return n_discard`**: Returns the integer count of samples to skip.

---

## 4. USRP B210 Hardware Setup

This function initializes the physical radio hardware.

```python
def setup_usrp(fc, fs, gain):
    print(f"[INFO] Connecting to USRP B210...")
    try:
        usrp = uhd.usrp.MultiUSRP("type=b200")
        usrp.set_clock_source("internal")
    except RuntimeError as e:
        print(f"[CRITICAL] USRP Connection Failed: {e}")
        print("Make sure the device is plugged in and recognized by 'uhd_find_devices'.")
        raise
```

* **`def setup_usrp(fc, fs, gain):`**: Defines function taking center frequency (`fc`), sample rate (`fs`), and gain (`gain`).
* **`print(...)`**: Informs the user that connection is starting.
* **`try:` ... `except RuntimeError as e:`**: A generic Python error handling block. If any code inside `try` fails, the `except` block runs.
* **`usrp = uhd.usrp.MultiUSRP("type=b200")`**: This is the core UHD command.
    * It attempts to find and connect to a connected USRP device matching the argument "type=b200" (which covers B200, B210, B200mini).
    * It returns a `usrp` object used to control the device.
* **`usrp.set_clock_source("internal")`**: Tells the USRP to use its own internal crystal oscillator for timing. (Alternative: "external" if using a GPSDO).
* **`raise`**: If the connection failed (`except` block), this command re-raises the error to stop the program immediately, as we cannot proceed without hardware.

```python
    print(f"[INFO] Configuring Radio: {fc/1e6:.3f} MHz, Rate: {fs/1e6:.3f} Msps...")
    
    tune_req = uhd.types.TuneRequest(fc)
    tune_req.args = uhd.types.DeviceAddr("mode_n=integer") 
    
    usrp.set_rx_rate(fs, 0)
    usrp.set_rx_freq(tune_req, 0)
    usrp.set_rx_gain(gain, 0)
    usrp.set_rx_bandwidth(fs, 0)

    time.sleep(1.0)
    return usrp
```

* **`tune_req = uhd.types.TuneRequest(fc)`**: Creates a tuning request object for the target frequency `fc`.
* **`tune_req.args = uhd.types.DeviceAddr("mode_n=integer")`**: Advanced tuning setting.
    * "Integer-N" tuning restricts the synthesizer to integer multiples of the reference frequency. It often provides better phase noise (cleaner signal) than fractional tuning, though it has less precise frequency steps.
* **`usrp.set_rx_rate(fs, 0)`**: Sets the Sample Rate for the receiver (channel 0).
* **`usrp.set_rx_freq(tune_req, 0)`**: Tunes the receiver (channel 0) to the frequency defined in `tune_req`.
* **`usrp.set_rx_gain(gain, 0)`**: Sets the analog gain (amplification) in dB.
* **`usrp.set_rx_bandwidth(fs, 0)`**: Sets the analog filter bandwidth on the device. Usually matched to the sample rate to filter out aliasing noise.
* **`time.sleep(1.0)`**: Pauses execution for 1 second. This is critical. After tuning or changing gain, the analog hardware (local oscillators, capacitors) needs time to stabilize before capturing valid data.
* **`return usrp`**: Returns the configured device object.

---

## 5. Capture Logic

This function manages the streaming of raw data from the device to the computer's memory.

```python
def capture_samples(usrp_dev, duration, fs):
    num_samps_target = int(np.ceil(duration * fs))
    
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    streamer = usrp_dev.get_rx_stream(st_args)
```

* **`num_samps_target = int(np.ceil(duration * fs))`**: Calculates exactly how many individual samples constitute the requested `duration`. (Time × Rate = Count).
* **`st_args = uhd.usrp.StreamArgs("fc32", "sc16")`**: Configures the data format for streaming.
    * `"fc32"` (CPU format): We want the data in Python as **Float Complex 32-bit** (standard `numpy.complex64`).
    * `"sc16"` (Wire format): Over the USB cable, data is sent as **Signed Complex 16-bit** integers to save bandwidth. The UHD driver automatically converts these to floats for us.
* **`streamer = usrp_dev.get_rx_stream(st_args)`**: Creates a `streamer` object specifically for receiving (RX) data with these settings.

```python
    max_samps = streamer.get_max_num_samps()
    recv_buffer = np.zeros((1, max_samps), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()
```

* **`max_samps = streamer.get_max_num_samps()`**: Asks the driver: "What is the biggest chunk of data you can give me at once?". This is usually the MTU size of the transport (e.g., a USB packet).
* **`recv_buffer`**: Allocates a temporary NumPy array to hold one incoming packet.
    * Shape `(1, max_samps)`: 1 channel, length `max_samps`.
    * `dtype=np.complex64`: Matches the "fc32" format requested above.
* **`metadata = uhd.types.RXMetadata()`**: Creates an object to hold metadata for each packet (timestamps, error codes like overflows).

```python
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
    stream_cmd.num_samps = num_samps_target
    stream_cmd.stream_now = True
    stream_cmd.time_spec = usrp_dev.get_time_now()

    print(f"[INFO] Capturing {duration}s ({num_samps_target} samples)...")
    streamer.issue_stream_cmd(stream_cmd)
```

* **`stream_cmd = uhd.types.StreamCMD(...)`**: Builds a command to tell the USRP when and how to stream.
* **`uhd.types.StreamMode.num_done`**: Tells the USRP: "Send a specific number of samples, then stop automatically."
* **`stream_cmd.num_samps`**: Specifies that exact number (`num_samps_target`).
* **`stream_cmd.stream_now = True`**: Tells the USRP to start immediately upon receipt.
* **`stream_cmd.time_spec`**: Not strictly used when `stream_now=True`, but good practice to initialize.
* **`streamer.issue_stream_cmd(stream_cmd)`**: Sends this command to the hardware. The USRP starts pushing data into the USB buffer immediately.

```python
    full_data = np.zeros(num_samps_target, dtype=np.complex64)
    samps_received = 0
    timeout_counter = 0

    while samps_received < num_samps_target:
        samps = streamer.recv(recv_buffer, metadata)
```

* **`full_data`**: Creates a large array to hold the *entire* capture (not just one packet).
* **`samps_received`**: Counter to track progress.
* **`while samps_received < num_samps_target:`**: Loops until we have collected all requested samples.
* **`samps = streamer.recv(recv_buffer, metadata)`**: This is the blocking call.
    * It tries to pull data from the USB buffer into our `recv_buffer`.
    * It returns `samps`, the number of valid samples actually written to the buffer (might be less than `max_samps`).
    * It populates `metadata` with status info.

```python
        if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
            print(f"[ERROR] {metadata.strerror()}")
            if metadata.error_code != uhd.types.RXMetadataErrorCode.overflow:
                break
```

* **`if metadata.error_code != ...`**: Checks if the packet was received cleanly.
* **`uhd.types.RXMetadataErrorCode.none`**: Means "No Error".
* **`metadata.strerror()`**: Prints a human-readable error string.
* **`overflow` (Check)**: An "Overflow" ("O" printed on console) means the computer wasn't reading fast enough and the USRP's internal buffer filled up. We usually warn but continue. Other errors (like timeout) usually require stopping (`break`).

```python
        if samps > 0:
            end_idx = min(samps_received + samps, num_samps_target)
            count = end_idx - samps_received
            full_data[samps_received:end_idx] = recv_buffer[0, :count]
            samps_received += count
            timeout_counter = 0
```

* **`if samps > 0:`**: If we got data...
* **`end_idx`**: Calculates where this chunk fits in the `full_data` array. `min` ensures we don't write past the end of the array if the USRP sends an extra packet.
* **`full_data[...] = recv_buffer[...]`**: Copies the data from the temporary packet buffer into the main storage array.
* **`samps_received += count`**: Updates our progress.
* **`timeout_counter = 0`**: Resets the timeout watch-dog because we successfully got data.

```python
        else:
            timeout_counter += 1
            if timeout_counter > 1000:
                print("[WARN] Timeout waiting for samples.")
                break

    print(f"[INFO] Capture Complete. Acquired {len(full_data)} samples.")
    return full_data
```

* **`else:`**: If `samps == 0` (no data returned in this call).
* **`timeout_counter` logic**: If we loop 1000 times without receiving *any* data, we assume the stream died and break the loop to prevent the program from freezing forever.
* **`return full_data`**: Returns the NumPy array containing the captured radio signal.

---

## 6. Signal Processing: Dynamic DC Blocker

This function applies the digital filter to remove the DC offset.

```python
def apply_dc_blocker(samples, fs):
    alpha = calculate_optim_alpha(DC_BLOCKER_CUTOFF_HZ, fs)
    
    n_discard = calculate_settling_samples(alpha)
    
    print(f"[INFO] DC Blocker Configured:")
    print(f"       -> Target Cutoff: {DC_BLOCKER_CUTOFF_HZ/1000} kHz")
    print(f"       -> Calculated Alpha: {alpha:.5f}")
    print(f"       -> Discarding First: {n_discard} samples (Settling Time)")
```

* **`apply_dc_blocker`**: Main processing function.
* Calls `calculate_optim_alpha` and `calculate_settling_samples` (explained in Section 3) to configure the filter dynamically based on the current `fs`.
* Prints the configuration for verification.

```python
    if len(samples) < n_discard + 100:
        print("[WARN] Data too short for this filter configuration!")
        return samples 
```

* **Check Data Length**: If the captured data is shorter than the number of samples we need to discard (plus a small buffer of 100), filtering is impossible or useless. It returns the raw samples to avoid a crash.

```python
    b = [1, -1]
    a = [1, -alpha]
    filtered = lfilter(b, a, samples)
    
    return filtered[n_discard:]
```

* **`b = [1, -1]`**: Numerator coefficients for a standard DC blocking IIR filter. This represents the difference equation part $y[n] = x[n] - x[n-1]$.
* **`a = [1, -alpha]`**: Denominator coefficients. This represents the feedback part involved in the pole location.
* **`lfilter(b, a, samples)`**: Applies the linear filter defined by `b` and `a` to the `samples` array.
* **`filtered[n_discard:]`**: Slices the array. It removes the first `n_discard` samples (which contain the transient distortion/garbage) and returns only the clean, settled data.

---

## 7. Visualization: Time Domain

Plots the raw waveform (Amplitude vs Time).

```python
def plot_time_domain(iq_data, fs, label):
    decimation = 100 
    subset = iq_data[::decimation]
    t = np.arange(len(subset)) * decimation / fs
```

* **`decimation = 100`**: Plotting millions of points is slow and visually crowded. We only keep every 100th sample.
* **`subset = iq_data[::decimation]`**: Uses NumPy slicing `[start:stop:step]` to select every 100th item.
* **`t = ...`**: Generates the time axis (x-axis).
    * `np.arange(len(subset))`: Creates [0, 1, 2, ... N].
    * `* decimation / fs`: Scales indices to seconds. (Sample Index / Sample Rate = Time).

```python
    plt.figure(figsize=(10, 3))
    plt.plot(t, np.abs(subset), label='Magnitude', color='#004488', linewidth=0.8)
    plt.title(f"Time Domain (Decimated) - {label}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
```

* **`plt.figure(...)`**: Creates a plot window of size 10x3 inches.
* **`plt.plot(t, np.abs(subset), ...)`**: Plots the data.
    * `np.abs(subset)`: IQ data is complex ($I + jQ$). `abs` calculates the magnitude $\sqrt{I^2 + Q^2}$ (envelope).
* **`plt.show()`**: Renders the plot to the screen.

---

## 8. Visualization: STFT

Calculates and plots the Spectrogram (Frequency vs Time vs Power).

```python
def compute_and_plot_block_stft(data, fs, fc, label):
    print("[INFO] Computing STFT...")
    
    Asl = TARGET_ATTENUATION_DB
```

* **`Asl`**: Short variable name for the side-lobe attenuation target defined in globals.

```python
    if Asl > 60:
        beta_val = 0.12438 * (Asl + 6.3)
    elif Asl > 13.26:
        beta_val = 0.76609 * (Asl - 13.26)**0.4 + 0.09834 * (Asl - 13.26)
    else:
        beta_val = 0.0
```

* **Kaiser Beta Calculation**: This logic implements the empirical formula for the Kaiser window parameter $\beta$.
    * This formula determines the shape of the window based on the desired attenuation (`Asl`).
    * If `Asl > 60`, a linear approximation is used.
    * If `13.26 < Asl < 60`, a polynomial approximation is used.
    * Below that, no windowing ($\beta=0$, rectangular) is used.

```python
    delta_ml = 2 * np.pi * (TARGET_RESOLUTION_HZ / fs)
    numerator = 24 * np.pi * (Asl + 12)
    denominator = 155 * delta_ml
    n_fft_calc = (numerator / denominator) + 1
    n_fft = int(np.ceil(n_fft_calc))
    if n_fft % 2 != 0: n_fft += 1
```

* **FFT Size Calculation**: This calculates the required FFT size (`n_fft`) to achieve the target frequency resolution (`TARGET_RESOLUTION_HZ`) given the chosen window attenuation.
    * This ensures the "Main Lobe Width" of the window fits within the resolution target.
    * **`if n_fft % 2 != 0: n_fft += 1`**: Ensures `n_fft` is even (FFTs are faster and easier to handle with even numbers).

```python
    hop_length = n_fft // 2
    window = np.kaiser(n_fft, beta=beta_val)
```

* **`hop_length`**: Determines the overlap. We move the window forward by `n_fft // 2` samples each time (50% overlap).
* **`np.kaiser`**: Generates the actual window array using the calculated length and beta.

```python
    n_samples = len(data)
    n_frames = (n_samples - n_fft) // hop_length + 1
    
    if n_frames <= 0:
        print("[ERROR] Data too short for analysis.")
        return

    spectrogram_data = np.zeros((n_fft, n_frames), dtype=np.float32)
```

* **`n_frames`**: Calculates how many "columns" (time slices) the spectrogram will have.
* **`spectrogram_data`**: Pre-allocates a 2D matrix to hold the result (Rows=Frequency bins, Columns=Time frames).

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

* **Loop**: Iterates through every time frame.
* **`chunk`**: Slices `n_fft` samples from the data.
* **`windowed`**: Multiplies the data chunk by the Kaiser window (tapers edges to zero).
* **`np.fft.fft`**: Computes the Fast Fourier Transform. Returns frequency domain data.
* **`np.fft.fftshift`**: Standard FFTs output [0..positive..negative] frequencies. `fftshift` rearranges them to [negative..0..positive], which is standard for plotting.
* **`mag_db`**: Converts magnitude to Decibels.
    * `np.log10`: Log base 10.
    * `+ 1e-12`: Adds a tiny number to prevent taking the log of zero (which results in -Infinity).
    * `20 *`: Factor for field quantities (voltage/amplitude).

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
```

* **`extent`**: Defines the physical units for the axes of the image: `[time_start, time_end, freq_min, freq_max]`.
* **`plt.imshow`**: Displays the 2D matrix as an image/heatmap.
    * `cmap='inferno'`: A color map where dark is low power, bright yellow is high power.
    * `origin='lower'`: Ensures low frequencies are at the bottom of the Y-axis.

---

## 9. Main Controller & Execution

This is the entry point of the script where the logic flow is orchestrated.

```python
def run_experiment(usrp, fc, bw, dwell, label):
    print(f"\n[TASK] Starting Run: {label}")
    
    usrp.set_rx_rate(bw, 0)
    usrp.set_rx_freq(uhd.types.TuneRequest(fc), 0)
    usrp.set_rx_bandwidth(bw, 0)
    
    time.sleep(1.0) 
    
    iq_data = capture_samples(usrp, dwell, bw)
    
    if len(iq_data) > 2000:
        iq_clean = apply_dc_blocker(iq_data, fs=bw)
        
        plot_time_domain(iq_clean, bw, label)
        compute_and_plot_block_stft(iq_clean, bw, fc, label)
    else:
        print("[ERROR] Not enough data captured.")
```

* **`run_experiment`**: A wrapper function to execute one full cycle: Retune -> Wait -> Capture -> Filter -> Plot.
* **`if len(iq_data) > 2000:`**: Only proceeds to plotting if meaningful data was actually captured.

```python
if __name__ == "__main__":
    try:
        usrp_dev = setup_usrp(2440e6, 20e6, 30)
        
        print("\n" + "="*50)
        print(f"   DYNAMIC ANALYZER (DC Cutoff: {DC_BLOCKER_CUTOFF_HZ} Hz)")
        print("="*50)
        
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
            
            fc = raw_fc * 1e9
            bw = raw_bw * 1e6
            label = f"{raw_fc}GHz_BW{raw_bw}M"
            
            run_experiment(usrp_dev, fc, bw, dwell, label)
            
    except KeyboardInterrupt:
        print("\n[INFO] User stopped the script.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
```

* **`if __name__ == "__main__":`**: Standard Python guard. Ensures this code only runs if the script is executed directly (not imported as a module).
* **`setup_usrp(2440e6, 20e6, 30)`**: Initializes the USRP once at startup (2.44 GHz, 20 MHz rate, 30 dB gain).
* **`while True:`**: Infinite loop to allow the user to run multiple experiments without restarting the script.
* **`input(...)`**: pauses and waits for user input from the keyboard.
    * **`or 20`**: Python trick. If the user just hits Enter (empty string), it defaults to 20.
* **`fc = raw_fc * 1e9`**: Converts user input (GHz) to Hz (e.g., 2.4 -> 2,400,000,000).
* **`except KeyboardInterrupt:`**: Catches `Ctrl+C`. This allows the script to exit gracefully instead of crashing with a traceback.
