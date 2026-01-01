# Code Documentation

## I. System Overview
This software implements a complete signal acquisition and analysis pipeline using a **USRP B210** software-defined radio. The system architecture is designed to capture In-Phase/Quadrature (IQ) samples, remove DC offsets using a dynamic High-Pass Filter (HPF), and visualize the signal in both the time domain and frequency domain (via Short-Time Fourier Transform).

## II. Detailed Module Analysis

### 1. Library Imports and Dependencies
The system relies on four primary external libraries:
* **`uhd`**: The official Python API for Ettus Research devices, handling hardware control and data streaming.
* **`numpy`**: Provides support for large, multi-dimensional arrays and matrices (`ndarray`), which are required for high-performance numerical computation of signal data.
* **`matplotlib.pyplot`**: A state-based interface for creating static, interactive, and animated visualizations in Python.
* **`scipy.signal`**: Contains tools for signal processing, specifically filter design (`lfilter`) and window generation (`get_window`).

### 2. Configuration and Helper Logic
**Code Block:** Section 1 & 2 (`calculate_optim_alpha`, `calculate_settling_samples`)

**Logic Explanation:**
To ensure the DC Blocker filter acts consistently regardless of the sampling rate chosen by the user, the script calculates filter coefficients dynamically.
* **`calculate_optim_alpha`**: Determines the filter smoothing factor ($\alpha$). The logic ensures that the filter's cutoff frequency remains fixed (e.g., at 25 kHz) even if the sampling rate changes between experiments.
* **`calculate_settling_samples`**: Infinite Impulse Response (IIR) filters require time to reach a steady state. This function calculates how many initial samples are "corrupted" by the filter's transient response so they can be discarded later.

**Syntax Analysis:**
* **`def function_name(params):`**: This defines a **function**, a reusable block of code.
* **`if fs <= 0:`**: A **conditional statement**. It executes the indented code block only if the condition is true.
* **`return value`**: Exits the function and sends the result back to the caller.
* **`np.pi`**: Accesses the mathematical constant $\pi$ from the NumPy library.
* **`np.ceil()`**: A NumPy function that rounds a number **up** to the nearest integer.
* **`int()`**: A **type cast**. It converts a floating-point number (e.g., 5.7) into an integer (e.g., 5) by truncating the decimal.

### 3. Hardware Initialization
**Code Block:** Section 3 (`setup_usrp`)

**Logic Explanation:**
This module establishes a connection to the USRP hardware.
1.  **Instantiation**: Creates a `MultiUSRP` object representing the physical radio.
2.  **Clocking**: Sets the time source to "internal" to use the on-board oscillator.
3.  **Tuning**: A `TuneRequest` object is created to handle the complex logic of tuning the Local Oscillator (LO) and the DSP chain. This is more robust than simply setting a float frequency.
4.  **Configuration**: Sets the sample rate, gain, and analog bandwidth.

**Syntax Analysis:**
* **`try: ... except RuntimeError as e:`**: This is **Exception Handling**. The code inside `try` is attempted. If an error (specifically a `RuntimeError`) occurs, the program does not crash; instead, it jumps to the `except` block to handle the error gracefully (e.g., printing a message).
* **`raise`**: Used inside an exception block to re-trigger the error after logging it, stopping the program if the radio cannot be found.
* **`f"..."` (f-string)**: Formatted string literals. Expressions inside `{}` are evaluated at runtime and inserted into the string. Example: `{fc/1e6:.3f}` takes the variable `fc`, divides by 1,000,000, and formats it to 3 decimal places.
* **Object Methods**: Syntax like `usrp.set_rx_rate(...)` calls a function that belongs specifically to the `usrp` object instance.

### 4. Data Acquisition Engine
**Code Block:** Section 4 (`capture_samples`)

**Logic Explanation:**
This function manages the streaming of data from the radio to the host computer's RAM.
1.  **Streamer Setup**: A "streamer" is initialized to interpret data formats (Complex Float 32-bit for host, Short Complex 16-bit for over-the-wire transport).
2.  **Buffer Allocation**: A pre-allocated NumPy array (`recv_buffer`) is created. This is efficient because it avoids creating new memory blocks repeatedly.
3.  **Command Issue**: A `StreamCMD` tells the radio to start sending a specific number of samples immediately.
4.  **Receive Loop**: The code enters a `while` loop. It repeatedly calls `streamer.recv()` to fill the buffer. These small chunks are copied into the main `full_data` array until the target sample count is reached.

**Syntax Analysis:**
* **`np.zeros((rows, cols), dtype=...)`**: Creates a new array filled with zeros. `dtype=np.complex64` specifies that each number in the array is a complex number (real + imaginary parts), which is standard for radio signals.
* **`while condition:`**: A loop that continues running as long as the condition is True.
* **`+=` Operator**: Increment assignment. `a += b` is shorthand for `a = a + b`.
* **`break`**: Immediately terminates the innermost loop it is currently in.
* **`[start:end]` (Slicing)**: Extracts a specific portion of an array. `full_data[0:100]` accesses the first 100 elements.

### 5. Signal Processing (DC Blocker)
**Code Block:** Section 5 (`apply_dc_blocker`)

**Logic Explanation:**
Raw radio signals often contain a "DC offset" (a spike at 0 Hz) due to hardware imperfections.
1.  **Filter Design**: The script defines the numerator (`b`) and denominator (`a`) coefficients for a difference equation (the mathematical representation of the filter).
2.  **Application**: `scipy.signal.lfilter` applies this linear filter to the data.
3.  **Transient Removal**: The beginning of the filtered signal is distorted while the filter stabilizes. The function slices off these initial samples (`n_discard`) to ensure data purity.

**Syntax Analysis:**
* **Lists `[...]`**: `[1, -1]` defines a Python list. Unlike NumPy arrays, lists are general-purpose containers.
* **`len(samples)`**: Returns the length (number of items) in the container.

### 6. Visualization: Time Domain
**Code Block:** Section 6 (`plot_time_domain`)

**Logic Explanation:**
Displays the amplitude of the signal over time.
1.  **Decimation**: Plotting millions of points is slow and visually indistinguishable. The code uses `subset = iq_data[::100]` to keep only every 100th sample.
2.  **Time Vector**: A time axis (`t`) is generated relative to the sampling rate so the X-axis shows seconds, not just index numbers.
3.  **Magnitude**: `np.abs()` computes the magnitude ($\sqrt{I^2 + Q^2}$) of the complex IQ data.

**Syntax Analysis:**
* **`[::decimation]`**: Extended slicing syntax `[start:stop:step]`. By omitting start and stop, it defaults to the whole array, taking every `100`th item.
* **`plt.figure`**: Initializes a blank canvas for plotting.
* **`plt.show()`**: Renders the active figure window to the user.

### 7. Visualization: Spectrogram (STFT)
**Code Block:** Section 7 (`compute_and_plot_block_stft`)

**Logic Explanation:**
This module performs a Short-Time Fourier Transform (STFT) to visualize how frequencies change over time.
1.  **Window Calculation**: A Kaiser window is generated. This window shape reduces "spectral leakage" (where energy from one frequency bleeds into others).
2.  **FFT Loop**: The code iterates through the data in chunks (frames).
    * It multiplies the chunk by the window.
    * It applies the Fast Fourier Transform (`np.fft.fft`) to convert time data to frequency data.
    * It shifts the zero-frequency component to the center of the array (`np.fft.fftshift`).
    * It converts the magnitude to the Logarithmic decibel scale (dB) for easier viewing.
3.  **Rendering**: The 2D matrix of results is plotted as an image/heatmap.

**Syntax Analysis:**
* **`//` (Floor Division)**: divides two numbers and discards the fractional part (e.g., `7 // 2` is `3`, not `3.5`).
* **`for i in range(n):`**: A loop that iterates `n` times. `i` takes values from `0` to `n-1`.
* **`[:, i]` (2D Slicing)**: Selects all rows (`:`) for the specific column `i`. Used here to insert a column of FFT data into the spectrogram matrix.
* **`np.log10()`**: Computes the base-10 logarithm.

### 8. Execution Flow (Main Controller)
**Code Block:** Section 8 & `__main__`

**Logic Explanation:**
The `run_experiment` function encapsulates a single test run (configure -> capture -> process -> plot).
The `if __name__ == "__main__":` block is the entry point. It ensures that this script runs only when executed directly, not when imported as a library. It contains an infinite loop (`while True`) that prompts the user for inputs (Frequency, Bandwidth) and runs experiments until the user inputs 0 to exit.

**Syntax Analysis:**
* **`input()`**: Pauses the program and waits for the user to type text and press Enter. The result is always a string.
* **`or` Operator**: `input(...) or 1.0`. If the user types nothing (an empty string, which evaluates to False), Python uses the value after the `or` (1.0). This is a concise way to set default values.
* **`KeyboardInterrupt`**: A specific exception triggered when the user presses `Ctrl+C`. This allows the script to exit cleanly rather than crashing with a traceback.
