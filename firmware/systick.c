
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/cm3/nvic.h>
#include <libopencm3/cm3/systick.h>
#include "systick.h"

static volatile uint32_t milliseconds;

void sys_tick_handler(void) {
    milliseconds++;
}

/* Set up a timer to create 1mS ticks. */
void systick_setup(void) {
    systick_set_clocksource(STK_CSR_CLKSOURCE_AHB);

    /* Check if the systick calibration value is accurate */
    if (STK_CALIB & STK_CALIB_SKEW) {
        /* the TENMS value is not accurate, estimate it based on the AHB 
         * value. (AHB / 1000) */
        systick_set_reload(rcc_ahb_frequency / 1000);
    } else {
        /* Get the systick calibration value, when the source is AHB this gives 
         * a 1msec tick rate. */
         systick_set_reload(systick_get_calib());
    }

    systick_counter_enable();
    systick_interrupt_enable();

    /* Set systick priority to maximum */
    nvic_set_priority(NVIC_SYSTICK_IRQ, 0xFF);
}

void systick_msleep(uint32_t delay) {
    uint32_t target = milliseconds + delay;
    while (target > milliseconds);
}

uint32_t systick_gettime(void) {
    return milliseconds;
}
