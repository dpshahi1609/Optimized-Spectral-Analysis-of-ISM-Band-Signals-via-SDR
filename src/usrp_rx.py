import uhd
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.signal import lfilter, get_window, kaiser_beta

# ==========================================
# 1. PARAMETERS & CONFIGURATION
# ==========================================
WINDOW_TYPE = 'kaiser' 
TARGET_ATTENUATION_DB = 74.0
TARGET_RESOLUTION_HZ = 25000.0 

# ==========================================
# 2. USRP B210 HARDWARE SETUP
# ==========================================
def setup_usrp(fc, fs, gain):
    print(f"[INFO] Connecting to USRP B210...")
    try:
        usrp = uhd.usrp.MultiUSRP("type=b200")
        usrp.set_clock_source("internal")
    except RuntimeError as e:
        print(f"[CRITICAL] USRP Connection Failed: {e}")
        print("Make sure the device is plugged in and recognized by 'uhd_find_devices'.")
        raise

    print(f"[INFO] Configuring Radio: {fc/1e6:.3f} MHz, Rate: {fs/1e6:.3f} Msps...")
    
    tune_req = uhd.types.TuneRequest(fc)
    tune_req.args = uhd.types.DeviceAddr("mode_n=integer") 
    
    usrp.set_rx_rate(fs, 0)
    usrp.set_rx_freq(tune_req, 0)
    usrp.set_rx_gain(gain, 0)
    usrp.set_rx_bandwidth(fs, 0)

    time.sleep(1.0)
    return usrp

# ==========================================
# 3. CAPTURE LOGIC
# ==========================================
def capture_samples(usrp_dev, duration, fs):
    num_samps_target = int(np.ceil(duration * fs))
    
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    streamer = usrp_dev.get_rx_stream(st_args)
    
    max_samps = streamer.get_max_num_samps()
    recv_buffer = np.zeros((1, max_samps), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()

    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
    stream_cmd.num_samps = num_samps_target
    stream_cmd.stream_now = True
    stream_cmd.time_spec = usrp_dev.get_time_now()

    print(f"[INFO] Capturing {duration}s ({num_samps_target} samples)...")
    streamer.issue_stream_cmd(stream_cmd)

    full_data = np.zeros(num_samps_target, dtype=np.complex64)
    samps_received = 0
    timeout_counter = 0

    while samps_received < num_samps_target:
        samps = streamer.recv(recv_buffer, metadata)

        if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
            print(f"[ERROR] {metadata.strerror()}")
            if metadata.error_code != uhd.types.RXMetadataErrorCode.overflow:
                break

        if samps > 0:
            end_idx = min(samps_received + samps, num_samps_target)
            count = end_idx - samps_received
            full_data[samps_received:end_idx] = recv_buffer[0, :count]
            samps_received += count
            timeout_counter = 0
        else:
            timeout_counter += 1
            if timeout_counter > 1000:
                print("[WARN] Timeout waiting for samples.")
                break

    print(f"[INFO] Capture Complete. Acquired {len(full_data)} samples.")
    return full_data

# ==========================================
# 4. SIGNAL PROCESSING: DC BLOCKER
# ==========================================
def apply_dc_blocker(samples, alpha=0.995):
    print("[INFO] Applying DC Offset Removal...")
    b = [1, -1]
    a = [1, -alpha]
    filtered = lfilter(b, a, samples)
    return filtered[1000:] if len(filtered) > 1000 else filtered

# ==========================================
# 5. VISUALIZATION: TIME DOMAIN
# ==========================================
def plot_time_domain(iq_data, fs, label):
    decimation = 100 
    subset = iq_data[::decimation]
    t = np.arange(len(subset)) * decimation / fs

    plt.figure(figsize=(10, 3))
    plt.plot(t, np.abs(subset), label='Magnitude', color='#004488', linewidth=0.8)
    plt.title(f"Time Domain (Decimated) - {label}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# ==========================================
# 6. VISUALIZATION: STFT
# ==========================================
def compute_and_plot_block_stft(data, fs, fc, label):
    print("[INFO] Computing STFT with Optimized Kaiser...")
    
    Asl = TARGET_ATTENUATION_DB
    
    if WINDOW_TYPE == 'kaiser':
        if Asl > 60:
            beta_val = 0.12438 * (Asl + 6.3)
        elif Asl > 13.26:
            beta_val = 0.76609 * (Asl - 13.26)**0.4 + 0.09834 * (Asl - 13.26)
        else:
            beta_val = 0.0
    else:
        beta_val = 0 

    if WINDOW_TYPE == 'kaiser':
        delta_ml = 2 * np.pi * (TARGET_RESOLUTION_HZ / fs)
        
        numerator = 24 * np.pi * (Asl + 12)
        denominator = 155 * delta_ml
        n_fft_calc = (numerator / denominator) + 1
        
        n_fft = int(np.ceil(n_fft_calc))
        
        if n_fft % 2 != 0: n_fft += 1
    else:
        n_fft = int(fs / TARGET_RESOLUTION_HZ)

    hop_length = n_fft // 2
    
    if WINDOW_TYPE == 'kaiser':
        window = np.kaiser(n_fft, beta=beta_val)
        win_str = f"Kaiser(beta={beta_val:.2f})"
    else:
        window = get_window(WINDOW_TYPE, n_fft)
        win_str = WINDOW_TYPE

    print(f"[INFO] Asl: {Asl}dB | Beta: {beta_val:.2f}")
    print(f"[INFO] FFT Size: {n_fft} (Increased to maintain resolution)")
    print(f"[INFO] Target Res: {TARGET_RESOLUTION_HZ/1000} kHz")

    n_samples = len(data)
    n_frames = (n_samples - n_fft) // hop_length + 1
    
    if n_frames <= 0:
        print("[ERROR] Data too short for analysis.")
        return

    spectrogram_data = np.zeros((n_fft, n_frames), dtype=np.float32)

    for i in range(n_frames):
        start = i * hop_length
        end = start + n_fft
        
        chunk = data[start:end]
        
        windowed = chunk * window
        fft_res = np.fft.fft(windowed)
        fft_shifted = np.fft.fftshift(fft_res)
        
        mag_db = 20 * np.log10(np.abs(fft_shifted) + 1e-12)
        spectrogram_data[:, i] = mag_db

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
    plt.title(f"Spectrogram | {label}\nBeta: {beta_val:.2f} | Res: {TARGET_RESOLUTION_HZ/1000} kHz") 
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (MHz)")
    plt.tight_layout()
    plt.show()

# ==========================================
# 7. MAIN CONTROLLER
# ==========================================
def run_experiment(usrp, fc, bw, dwell, label):
    print(f"\n[TASK] Starting Run: {label}")
    
    usrp.set_rx_rate(bw, 0)
    usrp.set_rx_freq(uhd.types.TuneRequest(fc), 0)
    usrp.set_rx_bandwidth(bw, 0)
    
    time.sleep(1.0) 
    
    iq_data = capture_samples(usrp, dwell, bw)
    
    if len(iq_data) > 2000:
        iq_clean = apply_dc_blocker(iq_data)
        plot_time_domain(iq_clean, bw, label)
        compute_and_plot_block_stft(iq_clean, bw, fc, label)
    else:
        print("[ERROR] Not enough data captured.")

if __name__ == "__main__":
    try:
        usrp_dev = setup_usrp(2440e6, 20e6, 30)
        
        print("\n" + "="*50)
        print(f"   OPTIMIZED ANALYZER (Target Attenuation: {TARGET_ATTENUATION_DB}dB)")
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
