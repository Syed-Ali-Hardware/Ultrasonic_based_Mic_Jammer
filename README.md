# Ultrasonic-Based Microphone Jammer

A research-based project exploring methods to jam microphones using ultrasonic transducers. This project implements multiple techniques to induce noise in microphone recordings, particularly targeting mobile phone microphones and other MEMS (Micro-Electro-Mechanical Systems) microphones.

## Table of Contents

- [Overview](#overview)
- [Research Background](#research-background)
- [How Ultrasonic Jamming Works](#how-ultrasonic-jamming-works)
- [Methods to Induce Noise in Microphones](#methods-to-induce-noise-in-microphones)
- [Hardware Implementation](#hardware-implementation)
- [Project Structure](#project-structure)
- [Applications](#applications)
- [Ethical Considerations](#ethical-considerations)
- [References and Further Reading](#references-and-further-reading)

## Overview

This project demonstrates how ultrasonic signals can be used to jam or interfere with microphone recordings on mobile phones and other devices. The implementation uses an ESP32 microcontroller to generate variable-frequency ultrasonic signals (1-6 kHz) with randomized duty cycles, creating effective interference patterns that disrupt audio recording capabilities.

**Key Features:**
- Variable frequency generation (1kHz to 6kHz)
- Randomized duty cycle patterns for enhanced jamming effectiveness
- Real-time mode switching with visual feedback
- ESP-IDF based implementation for ESP32
- Python simulation tools for waveform analysis

## Research Background

### The Science of Microphone Jamming

Modern mobile phones and recording devices primarily use MEMS (Micro-Electro-Mechanical Systems) microphones. These microphones work by detecting mechanical vibrations in their diaphragm and converting them into electrical signals. Research has shown that MEMS microphones are susceptible to ultrasonic interference due to several factors:

1. **Non-linear Response**: MEMS microphones exhibit non-linear behavior when exposed to high-intensity ultrasonic signals, causing distortion and saturation
2. **Intermodulation Distortion**: Multiple ultrasonic frequencies can create audible artifacts through intermodulation
3. **Mechanical Resonance**: The physical structure of MEMS microphones can resonate at certain ultrasonic frequencies
4. **ADC Saturation**: The analog-to-digital converter in the audio processing chain can saturate when exposed to ultrasonic signals

### Academic Foundation

This project builds upon research in acoustic security and privacy protection, including:
- Studies on MEMS microphone vulnerabilities to ultrasonic interference
- Research on non-audible acoustic attacks on voice-controlled systems
- Investigations into privacy protection methods using ultrasonic signals
- Analysis of frequency-dependent microphone response characteristics

## How Ultrasonic Jamming Works

### Principle of Operation

The ultrasonic jammer operates by emitting high-intensity sound waves at frequencies that, while inaudible or barely audible to humans, significantly affect microphone performance. The jamming effect is achieved through:

1. **Direct Saturation**: High-amplitude ultrasonic signals saturate the microphone's diaphragm, preventing it from accurately capturing target audio
2. **Harmonic Generation**: Non-linear distortion in the microphone creates audible harmonics and sub-harmonics
3. **Masking Effect**: The ultrasonic signal creates a noise floor that masks legitimate audio signals
4. **ADC Overload**: Ultrasonic components push the ADC into clipping, corrupting the digital audio signal

### Frequency Selection

The 1-6 kHz range used in this project is strategically chosen because:
- **1-4 kHz**: Overlaps with critical speech frequency bands, directly interfering with voice recording
- **4-6 kHz**: Near the upper limit of typical human hearing, making detection difficult while still affecting microphones
- **Variable Frequencies**: Prevents adaptive filtering and makes the jamming signal harder to remove in post-processing
- **MEMS Resonance**: Many MEMS microphones have resonant frequencies in this range

## Methods to Induce Noise in Microphones

This project implements multiple methods to maximize jamming effectiveness:

### 1. Variable Frequency Modulation

**Description**: The system cycles through six different frequency modes (1kHz, 2kHz, 3kHz, 4kHz, 5kHz, 6kHz) at regular intervals.

**Effectiveness**: 
- Prevents the microphone from adapting to a single interference frequency
- Covers a wider spectrum of microphone vulnerabilities
- Makes digital filtering more difficult

**Implementation**: Mode switching every 200ms with distinct frequency update rates

### 2. Randomized Duty Cycle Pattern

**Description**: Each frequency mode uses a 4096-element lookup table of randomized duty cycles ranging from 20% to 80%.

**Effectiveness**:
- Creates a noise-like signal that's difficult to filter out
- Prevents predictable patterns that could be removed
- Ensures consistent high-energy output without creating recognizable tones

**Implementation**: Hardware RNG generates unique patterns on each device power-up

### 3. PWM Carrier Modulation

**Description**: A 25 kHz PWM carrier is modulated by the 1-6 kHz signal with varying duty cycles.

**Effectiveness**:
- The 25 kHz carrier is completely inaudible to humans
- Modulation creates sidebands that affect microphone response across a wide frequency range
- Exploits non-linear characteristics of MEMS microphones

**Implementation**: LEDC peripheral generates precise PWM at 10-bit resolution

### 4. Ultrasonic Transducer Coupling

**Description**: Uses ultrasonic transducers connected to GPIO 25 to emit the jamming signal.

**Effectiveness**:
- Ultrasonic transducers have high directional gain
- Efficient conversion of electrical signal to acoustic pressure
- Can achieve high SPL (Sound Pressure Level) for effective jamming

**Implementation**: Direct connection to ESP32 GPIO with appropriate drive circuitry

### 5. Continuous Operation Mode

**Description**: The jammer operates continuously without gaps or pauses.

**Effectiveness**:
- Ensures no recording windows where clean audio could be captured
- Maintains constant acoustic pressure on target microphones
- Prevents voice-activated recording devices from capturing speech

**Implementation**: Zero-delay duty cycle updates with minimal CPU overhead

### 6. Acoustic Interference Patterns

**Description**: The combination of multiple frequencies and randomized patterns creates complex acoustic interference.

**Effectiveness**:
- Intermodulation products create additional jamming frequencies
- Phase interactions between different frequency components enhance disruption
- Creates a broadband noise signature that's difficult to characterize

**Implementation**: Fast mode switching with microsecond-precision timing

## Hardware Implementation

### Required Components

- **ESP32 Development Board**: Main microcontroller
- **Ultrasonic Transducers**: 25-40 kHz transducers recommended (e.g., 40 kHz piezoelectric transducers)
- **Driver Circuit**: Optional amplifier for increased output power
- **Power Supply**: 5V USB or battery pack for portable operation

### Connections

```
ESP32 GPIO 25  → Ultrasonic Transducer (+ optional driver circuit)
ESP32 GPIO 2   → Built-in LED (mode indicator)
ESP32 GND      → Ground
ESP32 5V       → Power supply
```

### Recommended Transducers

- **40 kHz Piezoelectric Transducers**: Common, inexpensive, effective
- **25 kHz Ultrasonic Speakers**: Better low-frequency response
- **Multiple Transducer Arrays**: For increased coverage and intensity

### Power Considerations

- Basic operation: ~100-200 mA
- With amplified transducers: 500 mA - 2A depending on driver circuit
- Battery operation: Use 18650 cells or power bank for portability

## Project Structure

```
Ultrasonic_based_Mic_Jammer/
├── README.md                           # This file - Project overview and documentation
└── ESP32_Variable_DUTY_IDF_1_to_6kHz/  # Main implementation
    ├── README.md                       # Technical documentation for ESP32 code
    ├── CMakeLists.txt                  # ESP-IDF build configuration
    ├── pwm_simulator.py                # Python simulation and analysis tool
    └── main/
        ├── CMakeLists.txt              # Main component build file
        └── main.c                      # Core implementation code
```

### Getting Started

#### Prerequisites

- ESP-IDF v4.0 or later
- ESP32 development board
- Ultrasonic transducers
- USB cable for programming

#### Building and Flashing

```bash
cd ESP32_Variable_DUTY_IDF_1_to_6kHz

# Configure the project (optional)
idf.py menuconfig

# Build the project
idf.py build

# Flash to ESP32
idf.py -p /dev/ttyUSB0 flash

# Monitor serial output
idf.py -p /dev/ttyUSB0 monitor
```

For detailed technical documentation, see [ESP32_Variable_DUTY_IDF_1_to_6kHz/README.md](ESP32_Variable_DUTY_IDF_1_to_6kHz/README.md)

#### Simulation and Analysis

The project includes a Python simulator for analyzing the generated waveforms:

```bash
cd ESP32_Variable_DUTY_IDF_1_to_6kHz
python3 pwm_simulator.py
```

This generates:
- Complete waveform visualization
- FFT analysis showing frequency components
- Spectrogram displaying frequency changes over time

## Applications

### Privacy Protection

- **Conference Rooms**: Prevent unauthorized recording of sensitive discussions
- **Private Conversations**: Protect personal conversations from nearby recording devices
- **Secure Facilities**: Add an extra layer of audio security to restricted areas

### Research and Development

- **Security Research**: Study vulnerabilities in audio recording systems
- **Testing**: Evaluate microphone performance under jamming conditions
- **Counter-Surveillance**: Research methods to detect and prevent covert audio recording

### Educational Purposes

- **Signal Processing**: Demonstrate frequency modulation and interference concepts
- **Acoustic Engineering**: Explore ultrasonic signal generation and propagation
- **Embedded Systems**: Learn ESP32 programming and PWM generation

## Ethical Considerations

### Responsible Use

This technology should be used **responsibly and legally**. Before deploying an ultrasonic jammer, consider:

1. **Legal Compliance**: Check local laws and regulations regarding jamming devices
2. **Consent**: Ensure all parties in the area are aware of and consent to the jamming
3. **Scope**: Limit jamming to the intended area to avoid affecting unintended devices
4. **Purpose**: Use only for legitimate privacy protection or research purposes

### Limitations

- **Range**: Ultrasonic signals are highly directional and limited in range (typically 1-5 meters)
- **Effectiveness**: May not work on all microphone types equally
- **Detection**: Can be detected with spectrum analyzers or ultrasonic detectors
- **Countermeasures**: Advanced recording systems may employ jamming detection and filtering

### Legal Disclaimer

**IMPORTANT**: This project is intended for educational and research purposes only. Users are responsible for ensuring their use complies with all applicable laws and regulations. The authors are not responsible for any misuse of this technology.

In many jurisdictions, jamming devices may be:
- Prohibited in public spaces
- Restricted to authorized personnel only
- Subject to specific licensing requirements
- Illegal to use without consent of all parties

**Always consult legal counsel before deploying jamming technology.**

## References and Further Reading

### Academic Papers

1. **"MEMS Microphone Vulnerabilities to Ultrasonic Signals"** - Research on non-linear response characteristics
2. **"Inaudible Voice Commands: The Long-Range Attack and Defense"** - Studies on ultrasonic attacks on voice systems
3. **"Acoustical Noise Jamming for Privacy Protection"** - Analysis of jamming effectiveness
4. **"Security Analysis of Voice-Controlled Systems"** - Exploration of acoustic attack vectors

### Technical Resources

- **ESP-IDF Documentation**: [https://docs.espressif.com/projects/esp-idf/](https://docs.espressif.com/projects/esp-idf/)
- **LEDC Peripheral Guide**: ESP32 LED PWM Controller documentation
- **Ultrasonic Transducer Datasheets**: Manufacturer specifications for various transducers
- **Signal Processing Fundamentals**: Books on FFT, modulation, and interference

### Related Projects

- **Ultrasonic Signal Generators**: Other ESP32/Arduino-based ultrasonic projects
- **Audio Privacy Tools**: Software and hardware solutions for audio security
- **MEMS Microphone Research**: Studies on microphone characteristics and vulnerabilities

## Contributing

Contributions to improve the jamming effectiveness, add new features, or enhance documentation are welcome. Please consider:

- Testing new frequency ranges or modulation patterns
- Implementing additional jamming methods
- Improving power efficiency
- Adding support for different hardware platforms
- Enhancing the simulation and analysis tools

## License

This project is provided as-is for educational and research purposes. Please review and comply with all applicable laws and regulations in your jurisdiction before use.

---

**Disclaimer**: This repository is for educational and research purposes only. The authors do not condone illegal surveillance or unauthorized jamming of recording devices. Users must ensure compliance with all applicable laws and obtain necessary permissions before deployment.
