#include <stdlib.h>
#include "main.h"
#include "timer.h"

static timer_handler_t isr_handler = NULL;

static void nvic_setup(void) {
    nvic_enable_irq(NVIC_TIM2_IRQ);
    nvic_set_priority(NVIC_TIM2_IRQ, 1);
}

void timer_setup(void) {
    nvic_setup();

    rcc_periph_clock_enable(RCC_TIM2);

    /* Reset TIM2 peripheral to defaults. */
    rcc_periph_reset_pulse(RST_TIM2);

    /* Internal clock source, counting up */
    timer_set_mode(TIM2, TIM_CR1_CKD_CK_INT, TIM_CR1_CMS_EDGE, TIM_CR1_DIR_UP);

    /* The timer will only be used once message Rx begins. */
    timer_one_shot_mode(TIM2);
}

void timer_config(timer_handler_t handler, uint16_t freq) {
    /* save the handler */
    isr_handler = handler;

    /* APB1 clock should be HSE (8MHz), and TIM2 clock = 2 * APB1 when the APB1 
     * prescaler is != 1 which I _think_ is the case (prescaler set in 
     * rcc_clock_setup_in_hse_8mhz_out_72mhz).
     *
     * Set the prescaler to count "bit times"
     */
    timer_set_prescaler(TIM2, ((rcc_apb1_frequency * 2) / freq));

    /* leave the timer and overflow ISR disabled for now */
}

void timer_start(uint32_t count) {
    /* Ensure that the timer is stopped */
    timer_stop();

    /* set the timeout count */
    timer_set_oc_value(TIM2, TIM_OC1, count);

    /* Start the EOM timer back at 0 */
    timer_set_counter(TIM2, 0);

    /* Ensure that the timer is enabled */
    timer_enable_counter(TIM2);

    /* Enable the TIM2 overflow ISR */
    timer_enable_irq(TIM2, TIM_DIER_CC1IE);
}

void timer_stop(void) {
    /* Stop the timer and the overflow interrupt */
    timer_disable_counter(TIM2);

    /* Disable the TIM2 overflow ISR */
    timer_disable_irq(TIM2, TIM_DIER_CC1IE);
}

void tim2_isr(void) {
    if (timer_get_flag(TIM2, TIM_SR_CC1IF)) {
        /* Clear compare interrupt flag. */
        timer_clear_flag(TIM2, TIM_SR_CC1IF);

        if (NULL != isr_handler) {
            /* Get the current counter value and pass it to the handler */
            isr_handler(timer_get_counter(TIM2));
        }
    }
}
