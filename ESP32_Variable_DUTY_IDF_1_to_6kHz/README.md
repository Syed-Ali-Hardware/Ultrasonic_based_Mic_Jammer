# ESP32 Variable Duty Cycle PWM Generator (1-6 kHz)

A high-precision PWM generator for ESP32 that cycles through 6 different frequency modes (1kHz to 6kHz) with randomized duty cycles. Designed for applications requiring variable frequency output with controlled duty cycle patterns.

## Features

- **6 Frequency Modes**: Automatically cycles through 1kHz, 2kHz, 3kHz, 4kHz, 5kHz, and 6kHz
- **Randomized Duty Cycles**: Uses a 4096-element lookup table with duty cycles ranging from 20% to 80%
- **Fast Mode Switching**: Configurable mode switching interval (default: 200ms minimum)
- **Visual Feedback**: LED blinks indicate current frequency mode (1 blink = 1kHz, 2 blinks = 2kHz, etc.)
- **High-Resolution PWM**: 10-bit resolution (0-1023) using LEDC peripheral
- **Optimized Timing**: Precise microsecond-level timing for accurate frequency generation

## Hardware Configuration

### GPIO Pins
- **GPIO 25**: PWM output signal
- **GPIO 2**: Built-in LED indicator (mode feedback)

### PWM Specifications
- **Base Timer Frequency**: 25 kHz
- **Duty Resolution**: 10-bit (1024 levels)
- **Duty Cycle Range**: 20% - 80% (randomized)
- **Output Frequencies**: 1, 2, 3, 4, 5, 6 kHz

## How It Works

### Frequency Generation
The system generates different frequencies by updating the duty cycle at specific intervals:
- **1 kHz**: Updates every 1000 µs
- **2 kHz**: Updates every 500 µs
- **3 kHz**: Updates every 333 µs
- **4 kHz**: Updates every 250 µs
- **5 kHz**: Updates every 200 µs
- **6 kHz**: Updates every 166 µs

### Mode Cycling
Every 200ms (configurable via `MODE_SWITCH_TIME_MS`), the system:
1. Advances to the next frequency mode
2. Blinks the LED to indicate the new mode (number of blinks = frequency in kHz)
3. Continues outputting PWM at the new frequency

### Random Duty Cycle Pattern
- A 4096-entry lookup table is generated at startup using ESP32's hardware RNG
- Each entry contains a duty cycle value between 51-204 (20%-80% of 255)
- Values are scaled to 10-bit resolution for LEDC peripheral
- The pattern loops continuously during operation

## Building and Flashing

### Prerequisites
- ESP-IDF v4.0 or later
- ESP32 development board

### Build Commands
```bash
# Configure the project (optional)
idf.py menuconfig

# Build the project
idf.py build

# Flash to ESP32
idf.py -p /dev/ttyUSB0 flash

# Monitor serial output
idf.py -p /dev/ttyUSB0 monitor

# Build, flash and monitor in one command
idf.py -p /dev/ttyUSB0 flash monitor
```

## Configuration

Key parameters can be modified in `main/main.c`:

```c
#define OUTPUT_GPIO         GPIO_NUM_25  // PWM output pin
#define LED_GPIO            GPIO_NUM_2   // LED indicator pin
#define MODE_SWITCH_TIME_MS 200          // Mode switching interval (ms)
#define TABLE_SIZE          4096         // Random pattern size
#define DUTY_MIN            51           // Minimum duty (20% of 255)
#define DUTY_MAX            204          // Maximum duty (80% of 255)
```

## Project Structure

```
├── CMakeLists.txt              # Top-level CMake configuration
├── main/
│   ├── CMakeLists.txt          # Main component CMake file
│   └── main.c                  # Main application code
├── pwm_simulator.py            # Python simulator for testing
└── README.md                   # This file
```

## Serial Output

Upon startup, the program outputs:
```
ESP32 Variable Duty Cycle Generator
Frequencies: 1kHz, 2kHz, 3kHz, 4kHz, 5kHz, 6kHz
Mode switch interval: 200 ms
Switching to mode 0 (1 kHz)
Switching to mode 1 (2 kHz)
...
```

## Applications

This project is suitable for:
- Audio jamming or masking applications
- Ultrasonic signal generation
- Motor control with variable frequency
- Testing and characterization of frequency-dependent systems
- Signal processing research and development

## Technical Notes

- Uses ESP-IDF's LEDC (LED Control) peripheral for hardware PWM generation
- Employs `esp_timer` for microsecond-precision timing
- Implements minimal-delay LED feedback (30ms per blink cycle)
- Includes watchdog prevention with periodic task yielding
- Zero-copy duty cycle updates for maximum performance
