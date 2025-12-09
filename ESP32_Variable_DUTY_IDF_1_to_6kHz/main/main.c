#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_random.h"

// GPIO Pin Definitions
#define OUTPUT_GPIO     GPIO_NUM_25  // PWM output pin
#define LED_GPIO        GPIO_NUM_2   // LED indicator (built-in LED on most ESP32 boards)

// LEDC Configuration
#define LEDC_TIMER              LEDC_TIMER_0
#define LEDC_MODE               LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL            LEDC_CHANNEL_0
#define LEDC_DUTY_RES           LEDC_TIMER_10_BIT // 10-bit resolution (0-1023)
#define LEDC_BASE_FREQ          25000            // 25kHz base frequency

// Mode switching time in milliseconds (supports minimum 200ms)
#define MODE_SWITCH_TIME_MS     200

// Frequency modes: 1kHz, 2kHz, 3kHz, 4kHz, 5kHz, 6kHz
#define NUM_MODES               6

// Random table configuration
#define TABLE_SIZE 4096
#define DUTY_MIN   51     // 20% of 255
#define DUTY_MAX   204    // 80% of 255

// Dynamically generated randomized duty cycle pattern
uint8_t randomized[TABLE_SIZE];

// Function to generate random table
void generateRandomTable(void) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        randomized[i] = (esp_random() % (DUTY_MAX - DUTY_MIN + 1)) + DUTY_MIN;
    }
}

// Fast LED blink function with minimal delay
void blink_led_fast(uint8_t times) {
    // Use very short pulses for minimal impact on mode switching
    for (uint8_t i = 0; i < times; i++) {
        gpio_set_level(LED_GPIO, 1);
        esp_rom_delay_us(15000);  // 15ms on
        gpio_set_level(LED_GPIO, 0);
        esp_rom_delay_us(15000);  // 15ms off
    }
    // No final delay to minimize total time
}

// Function to scale duty cycle value from DUTY_MIN-DUTY_MAX range to 10-bit LEDC range
static inline uint32_t scale_duty(uint8_t value) {
    // Input: 51-204 (20%-80% of 255), Output: ~204-819 (20%-80% of 1023)
    // Formula: (value * 1023) / 255
    return (value * 1023) / 255;
}

// Initialize LEDC peripheral
void ledc_init(void) {
    // Prepare and then apply the LEDC PWM timer configuration
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = LEDC_MODE,
        .timer_num        = LEDC_TIMER,
        .duty_resolution  = LEDC_DUTY_RES,
        .freq_hz          = LEDC_BASE_FREQ,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledc_timer));

    // Prepare and then apply the LEDC PWM channel configuration
    ledc_channel_config_t ledc_channel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LEDC_CHANNEL,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = OUTPUT_GPIO,
        .duty           = 0,
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledc_channel));
}

void app_main(void) {
    uint16_t sequence = 0;
    uint8_t mode = 0;  // 0=1kHz, 1=2kHz, 2=3kHz, 3=4kHz, 4=5kHz, 5=6kHz
    int64_t last_mode_switch = 0;
    int64_t last_update = 0;

    // Initialize LED GPIO
    gpio_reset_pin(LED_GPIO);
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);

    // Initialize LEDC for PWM output
    ledc_init();

    // Generate random duty cycle table
    generateRandomTable();

    // Initial blink indicator
    blink_led_fast(1);

    printf("ESP32 Variable Duty Cycle Generator\n");
    printf("Frequencies: 1kHz, 2kHz, 3kHz, 4kHz, 5kHz, 6kHz\n");
    printf("Mode switch interval: %d ms\n", MODE_SWITCH_TIME_MS);

    last_mode_switch = esp_timer_get_time();
    last_update = esp_timer_get_time();

    while (1) {
        int64_t now = esp_timer_get_time();

        // Calculate update interval in microseconds based on mode
        // Mode 0 (1kHz): update every 1000 us
        // Mode 1 (2kHz): update every 500 us
        // Mode 2 (3kHz): update every 333 us
        // Mode 3 (4kHz): update every 250 us
        // Mode 4 (5kHz): update every 200 us
        // Mode 5 (6kHz): update every 166 us
        uint32_t update_interval_us;
        switch(mode) {
            case 0: update_interval_us = 1000; break;  // 1 kHz
            case 1: update_interval_us = 500;  break;  // 2 kHz
            case 2: update_interval_us = 333;  break;  // 3 kHz
            case 3: update_interval_us = 250;  break;  // 4 kHz
            case 4: update_interval_us = 200;  break;  // 5 kHz
            case 5: update_interval_us = 166;  break;  // 6 kHz
            default: update_interval_us = 1000; break;
        }

        // Update duty cycle at the correct rate
        if ((now - last_update) >= update_interval_us) {
            last_update = now;
            
            uint8_t pulsewidth = randomized[sequence++];
            if (sequence >= TABLE_SIZE) {
                sequence = 0;
            }

            uint32_t duty = scale_duty(pulsewidth);
            ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, duty);
            ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
        }

        // Check if it's time to switch modes
        if ((now - last_mode_switch) >= (MODE_SWITCH_TIME_MS * 1000)) {
            last_mode_switch = now;
            mode++;
            if (mode >= NUM_MODES) {
                mode = 0;  // Loop back to 1kHz
            }
            
            printf("Switching to mode %d (%d kHz)\n", mode, mode + 1);
            blink_led_fast(mode + 1);  // Visual feedback with minimal delay
        }

        // Periodically yield CPU to prevent watchdog timeout
        // Delay only 1 tick (~10ms) every few iterations to maintain timing accuracy
        static uint16_t yield_counter = 0;
        if (++yield_counter >= 100) {  // Yield every 100 loops
            yield_counter = 0;
            vTaskDelay(1);  // 1 tick delay to allow IDLE task to run
        }
    }
}