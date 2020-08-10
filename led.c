#include "main.h"
#include "led.h"

static void gpio_setup(void) {
    /* Enable GPIOC clock for the LED. */
    rcc_periph_clock_enable(RCC_GPIOC);

    /* GPIO PC13 is the user controllable LED */
    gpio_set_mode(GPIOC, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO13);
}

void led_setup(void) {
    gpio_setup();

    led_off();
}

void led_toggle(void) {
    gpio_toggle(GPIOC, GPIO13);
}

void led_on(void) {
    gpio_clear(GPIOC, GPIO13);
}

void led_off(void) {
    gpio_set(GPIOC, GPIO13);
}
