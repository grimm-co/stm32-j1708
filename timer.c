#include <stdlib.h>
#include "main.h"
#include "timer.h"
#include "j1708.h"

static timer_handler_t tim2_handler = NULL;
static timer_handler_t tim3_handler = NULL;

static void timer_config(uint32_t timer_peripheral, uint32_t freq, uint32_t period) {
    timer_set_prescaler(timer_peripheral, (rcc_apb1_frequency * 2) / freq);

    timer_one_shot_mode(timer_peripheral);
    //timer_continuous_mode(timer_peripheral);

    //timer_set_period(timer_peripheral, J1708_BAUD * J1708_MSG_TIMEOUT);
    timer_enable_preload(timer_peripheral);

    timer_enable_oc_preload(timer_peripheral, TIM_OC1);
    timer_set_oc_mode(timer_peripheral, TIM_OC1, TIM_OCM_FROZEN);
    /* preload target value */
    timer_set_period(timer_peripheral, period);

    /* Initial target value */
    timer_set_oc_value(timer_peripheral, TIM_OC1, period);
}

void timer_setup(void) {
    rcc_periph_clock_enable(RCC_TIM2);
    nvic_enable_irq(NVIC_TIM2_IRQ);
    rcc_periph_reset_pulse(RST_TIM2);
    timer_set_mode(TIM2, TIM_CR1_CKD_CK_INT, TIM_CR1_CMS_EDGE, TIM_CR1_DIR_UP);

    nvic_enable_irq(NVIC_TIM3_IRQ);
    rcc_periph_clock_enable(RCC_TIM3);
    rcc_periph_reset_pulse(RST_TIM3);
    timer_set_mode(TIM3, TIM_CR1_CKD_CK_INT, TIM_CR1_CMS_EDGE, TIM_CR1_DIR_UP);

    /* The timer source is rcc_apb1_frequency * 2, we want to ensure that the 
     * prescaler allows for accurately counting 9600 baud signals and also fits 
     * within a 16-bit value, so set the frequency to be 48khz. This will count 
     * 5 per 9600 baud "bit time"
     *
     * TIM2: end of message timer - 10 "bit times" (@ 9600 baud) */
    timer_config(TIM2, 48000, J1708_MSG_TIMEOUT * 5);

    /* TIM3: collision wait/retry timer - EOM timeout + (priority * 2) */
    timer_config(TIM3, 48000, J1708_COLLISION_WAIT * 5);
}

void timer_set_handler(uint32_t timer_peripheral, timer_handler_t handler) {
    if (TIM2 == timer_peripheral) {
        tim2_handler = handler;
    } else if (TIM3 == timer_peripheral) {
        tim3_handler = handler;
    }
}

void timer_start(uint32_t timer_peripheral) {
    timer_enable_counter(timer_peripheral);
    timer_enable_irq(timer_peripheral, TIM_DIER_UIE);
}

void timer_stop(uint32_t timer_peripheral) {
    timer_disable_irq(timer_peripheral, TIM_DIER_UIE);
    timer_disable_counter(timer_peripheral);
}

void timer_restart(uint32_t timer_peripheral) {
    timer_set_counter(timer_peripheral, 0);
    timer_start(timer_peripheral);
}

void tim2_isr(void) {
    if (timer_get_flag(TIM2, TIM_SR_UIF)) {
        timer_clear_flag(TIM2, TIM_SR_UIF);

        if (NULL != tim2_handler) {
            tim2_handler();
        }
    }
}

void tim3_isr(void) {
    if (timer_get_flag(TIM3, TIM_SR_UIF)) {
        timer_clear_flag(TIM3, TIM_SR_UIF);

        if (NULL != tim3_handler) {
            tim3_handler();
        }
    }
}
