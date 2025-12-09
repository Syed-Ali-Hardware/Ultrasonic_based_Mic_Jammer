"""
ESP32 Variable Duty Cycle PWM Generator Simulator
Simulates the output waveform and FFT analysis of the PWM generator
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import signal

# Configuration (matching the ESP32 code)
LEDC_BASE_FREQ = 25000  # 25 kHz base PWM frequency
MODE_SWITCH_TIME_MS = 200  # Mode switch interval in milliseconds
NUM_MODES = 6  # 6 frequency modes (1kHz to 6kHz)
TABLE_SIZE = 4096  # Random table size
DUTY_MIN = 51  # 20% of 255
DUTY_MAX = 204  # 80% of 255
SIMULATION_TIME = 1.5  # 1.5 seconds of simulation

# Frequency modes update rates (in Hz)
MODE_FREQUENCIES = [1000, 2000, 3000, 4000, 5000, 6000]  # 1-6 kHz

# Generate random duty cycle table (matching ESP32 random generation)
np.random.seed(42)  # For reproducible results
randomized = np.random.randint(DUTY_MIN, DUTY_MAX + 1, TABLE_SIZE)

def scale_duty(value):
    """Scale duty cycle value from DUTY_MIN-DUTY_MAX range to 0-1 range"""
    # Input: 51-204 (20%-80% of 255), Output: 0.2-0.8
    return (value / 255.0)

def generate_pwm_waveform(duration):
    """Generate the complete PWM waveform for the specified duration"""
    
    # Sampling rate: much higher than PWM frequency for accurate representation
    sampling_rate = LEDC_BASE_FREQ * 20  # 500 kHz
    num_samples = int(duration * sampling_rate)
    time_array = np.linspace(0, duration, num_samples)
    waveform = np.zeros(num_samples)
    
    # Track current state
    current_mode = 0
    sequence_index = 0
    last_mode_switch_time = 0
    last_update_time = 0
    current_duty = scale_duty(randomized[0])
    
    print(f"Generating {duration}s waveform...")
    print(f"Sampling rate: {sampling_rate} Hz")
    print(f"Total samples: {num_samples}")
    
    # Generate waveform sample by sample
    for i, t in enumerate(time_array):
        t_ms = t * 1000  # Convert to milliseconds
        
        # Check if we need to switch modes
        if t_ms - last_mode_switch_time >= MODE_SWITCH_TIME_MS:
            last_mode_switch_time = t_ms
            current_mode = (current_mode + 1) % NUM_MODES
            if i % (num_samples // 20) == 0:  # Print progress
                print(f"Time: {t:.2f}s, Mode: {current_mode} ({MODE_FREQUENCIES[current_mode]} Hz)")
        
        # Update interval in microseconds for current mode
        update_interval_us = 1000000 / MODE_FREQUENCIES[current_mode]
        
        # Check if we need to update duty cycle
        if (t * 1e6) - last_update_time >= update_interval_us:
            last_update_time = t * 1e6
            current_duty = scale_duty(randomized[sequence_index])
            sequence_index = (sequence_index + 1) % TABLE_SIZE
        
        # Generate PWM signal: square wave at 25kHz with current duty cycle
        pwm_phase = (t * LEDC_BASE_FREQ) % 1.0
        waveform[i] = 1.0 if pwm_phase < current_duty else 0.0
    
    print("Waveform generation complete!")
    return time_array, waveform

def plot_waveform_and_fft(time_array, waveform):
    """Plot the waveform and its FFT analysis"""
    
    sampling_rate = len(time_array) / (time_array[-1] - time_array[0])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Full waveform (5 seconds)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time_array, waveform, linewidth=0.5, color='blue')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Complete 5-Second PWM Waveform with Mode Transitions')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, SIMULATION_TIME)
    
    # Add mode transition markers
    mode_switch_times = np.arange(MODE_SWITCH_TIME_MS / 1000, SIMULATION_TIME, MODE_SWITCH_TIME_MS / 1000)
    for i, t in enumerate(mode_switch_times):
        mode_num = (i + 1) % NUM_MODES
        ax1.axvline(x=t, color='red', linestyle='--', alpha=0.3, linewidth=1)
        ax1.text(t, 0.95, f'{MODE_FREQUENCIES[mode_num]}Hz', 
                rotation=90, verticalalignment='top', fontsize=8)
    
    # 2. Zoomed waveform (first 50ms to see PWM detail)
    ax2 = fig.add_subplot(gs[1, 0])
    zoom_mask = time_array < 0.01
    ax2.plot(time_array[zoom_mask] * 1000, waveform[zoom_mask], linewidth=0.8, color='green')
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('Zoomed View: First 10ms (showing 25kHz carrier and 1kHz modulation)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Even more zoomed (first 5ms to see individual PWM cycles)
    ax3 = fig.add_subplot(gs[1, 1])
    zoom_mask2 = time_array < 0.001
    ax3.plot(time_array[zoom_mask2] * 1000, waveform[zoom_mask2], linewidth=1, color='purple')
    ax3.set_xlabel('Time (ms)')
    ax3.set_ylabel('Amplitude')
    ax3.set_title('Ultra Zoom: First 1ms (individual 25kHz PWM cycles)')
    ax3.grid(True, alpha=0.3)
    
    # 4. FFT Analysis
    ax4 = fig.add_subplot(gs[2, :])
    
    # Compute FFT
    print("Computing FFT...")
    fft_result = np.fft.fft(waveform)
    frequencies = np.fft.fftfreq(len(waveform), 1/sampling_rate)
    
    # Get positive frequencies only
    positive_freq_mask = frequencies > 0
    frequencies = frequencies[positive_freq_mask]
    magnitude = np.abs(fft_result[positive_freq_mask])
    
    # Convert to dB scale
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    # Plot FFT
    ax4.plot(frequencies, magnitude_db, linewidth=0.5, color='red')
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Magnitude (dB)')
    ax4.set_title('FFT Analysis - Frequency Spectrum (showing 25kHz carrier and 1-6kHz modulation)')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 30000)  # Show up to 30kHz to see carrier and harmonics
    
    # Mark important frequencies
    ax4.axvline(x=LEDC_BASE_FREQ, color='blue', linestyle='--', alpha=0.5, linewidth=2, label='25kHz Carrier')
    for i, freq in enumerate(MODE_FREQUENCIES):
        ax4.axvline(x=freq, color='green', linestyle=':', alpha=0.5, linewidth=1.5)
        ax4.text(freq, ax4.get_ylim()[1] * 0.95, f'{freq}Hz', 
                rotation=90, verticalalignment='top', fontsize=7)
    
    ax4.legend()
    
    plt.suptitle('ESP32 Variable Duty Cycle PWM Generator - Waveform Analysis', 
                 fontsize=14, fontweight='bold')
    
    print("Plotting complete!")
    plt.tight_layout()
    plt.show()

def plot_spectrogram(time_array, waveform):
    """Plot spectrogram to show frequency changes over time"""
    
    sampling_rate = len(time_array) / (time_array[-1] - time_array[0])
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Compute spectrogram
    print("Computing spectrogram...")
    nperseg = int(sampling_rate * 0.05)  # 50ms segments
    f, t, Sxx = signal.spectrogram(waveform, sampling_rate, nperseg=nperseg)
    
    # Plot spectrogram
    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_xlabel('Time (s)')
    ax.set_title('Spectrogram - Frequency Content Over Time')
    ax.set_ylim(0, 30000)  # Focus on 0-30kHz range
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Power (dB)')
    
    # Add mode transition markers
    mode_switch_times = np.arange(MODE_SWITCH_TIME_MS / 1000, SIMULATION_TIME, MODE_SWITCH_TIME_MS / 1000)
    for i, time_mark in enumerate(mode_switch_times):
        mode_num = (i + 1) % NUM_MODES
        ax.axvline(x=time_mark, color='red', linestyle='--', alpha=0.5, linewidth=1)
        ax.text(time_mark, 28000, f'{MODE_FREQUENCIES[mode_num]}Hz', 
                rotation=90, verticalalignment='top', fontsize=8, color='white')
    
    plt.tight_layout()
    plt.show()

def main():
    """Main simulation function"""
    print("="*60)
    print("ESP32 Variable Duty Cycle PWM Generator Simulator")
    print("="*60)
    print(f"Configuration:")
    print(f"  PWM Carrier Frequency: {LEDC_BASE_FREQ} Hz")
    print(f"  Modulation Frequencies: {MODE_FREQUENCIES} Hz")
    print(f"  Mode Switch Interval: {MODE_SWITCH_TIME_MS} ms")
    print(f"  Duty Cycle Range: {DUTY_MIN/255*100:.1f}% - {DUTY_MAX/255*100:.1f}%")
    print(f"  Simulation Duration: {SIMULATION_TIME} seconds")
    print("="*60)
    
    # Generate waveform
    time_array, waveform = generate_pwm_waveform(SIMULATION_TIME)
    
    # Calculate some statistics
    avg_duty = np.mean(waveform)
    print(f"\nWaveform Statistics:")
    print(f"  Average Duty Cycle: {avg_duty*100:.2f}%")
    print(f"  Min Value: {np.min(waveform):.3f}")
    print(f"  Max Value: {np.max(waveform):.3f}")
    print(f"  RMS Value: {np.sqrt(np.mean(waveform**2)):.3f}")
    
    # Plot results
    plot_waveform_and_fft(time_array, waveform)
    
    # Plot spectrogram
    plot_spectrogram(time_array, waveform)

if __name__ == "__main__":
    main()
