#include <Arduino.h>
#include "OneShotHardwareTimer.h"
#include "led.h"

/* This is adapted from:
 *  https://github.com/stm32duino/Arduino_Core_STM32/blob/1.9.0/cores/arduino/HardwareTimer.cpp
 *
 * But adapted to remove all the unnecessary layers and indirection which do 
 * nothing useful except make the design of the timer IRQ handlers overly 
 * complex.
 *
 * For example, class only supports catching the update interrupt, so there is 
 * no reason to do all the other indirection and crap.  In addition this only 
 * supports the general purpose timers on the STM32F103C8 (TIM2-TIM4).
 *
 * As much as I'd like to avoid re-inventing the wheel the STM32duino timer HAL 
 * layer is a mess and I removed all of it. */

extern "C" {
    /* This array in theory supports all possible TIMER??_INDEX values, but we 
     * restrict it to only the valid general purpose timers:
     *      TIMER2_INDEX to TIMER5_INDEX
     * The full array is here because it makes the code simpler. */
    static callback_function_t isrCallbacks[TIMER_NUM] = { NULL };

    void TIM2_IRQHandler(void)
    {
        if (LL_TIM_IsActiveFlag_UPDATE(TIM2)) {
            LL_TIM_ClearFlag_UPDATE(TIM2);

            if (NULL != isrCallbacks[TIMER2_INDEX]) {
                isrCallbacks[TIMER2_INDEX]();
            }
        }
    }

    void TIM3_IRQHandler(void)
    {
        if (LL_TIM_IsActiveFlag_UPDATE(TIM3)) {
            LL_TIM_ClearFlag_UPDATE(TIM3);

            if (NULL != isrCallbacks[TIMER3_INDEX]) {
                isrCallbacks[TIMER3_INDEX]();
            }
        }
    }

    void TIM4_IRQHandler(void)
    {
        if (LL_TIM_IsActiveFlag_UPDATE(TIM4)) {
            LL_TIM_ClearFlag_UPDATE(TIM4);

            if (NULL != isrCallbacks[TIMER4_INDEX]) {
                isrCallbacks[TIMER4_INDEX]();
            }
        }
    }

#if 0
    void TIM5_IRQHandler(void)
    {
        if (LL_TIM_IsActiveFlag_UPDATE(TIM5)) {
            LL_TIM_ClearFlag_UPDATE(TIM5);

            if (NULL != isrCallbacks[TIMER5_INDEX]) {
                isrCallbacks[TIMER5_INDEX]();
            }
        }
    }
#endif
}

static void blinkError(uint32_t error) {
    /* Error blink codes: 3 short pulses */
    while (true) {
        /* short pulse for each value in the error */
        for (uint32_t i = 0; i < error; i++) {
            led_on();
            delay(200);
            led_off();
            delay(200);
        }

        /* Longer delay between loops */
        delay(1000);
    }
}

OneShotHardwareTimer::OneShotHardwareTimer(TIM_TypeDef *instance) {
    /* Configure which timer this object references, the hardware will be 
     * initialized later. */
    if (instance == TIM2) {
        _tim = instance;
        _idx = TIMER2_INDEX;

    } else if (instance == TIM3) {
        _tim = instance;
        _idx = TIMER3_INDEX;

    } else if (instance == TIM4) {
        _tim = instance;
        _idx = TIMER4_INDEX;

#if 0
    } else if (instance == TIM5) {
        _tim = instance;
        _idx = TIMER5_INDEX;
#endif

    } else {
        /* If this timer isn't supported just set instance to NULL which will 
         * produce an error soon enough. */
        _tim = NULL;
        _idx = UNKNOWN_TIMER;
    }
}

void OneShotHardwareTimer::configure(uint32_t freq, uint32_t period, callback_function_t callback) {
    /* First configure the RCC and NVIC settings for this timer.
     * After enabling the timer peripheral and the NVIC interrupt source send 
     * a reset pulse to the peripheral to force it back to original settings. */
    if (_tim == TIM2) {
        __HAL_RCC_TIM2_CLK_ENABLE();
        HAL_NVIC_EnableIRQ(TIM2_IRQn);
        __HAL_RCC_TIM2_FORCE_RESET();
        __HAL_RCC_TIM2_RELEASE_RESET();

    } else if (_tim == TIM3) {
        __HAL_RCC_TIM3_CLK_ENABLE();
        HAL_NVIC_EnableIRQ(TIM3_IRQn);
        __HAL_RCC_TIM3_FORCE_RESET();
        __HAL_RCC_TIM3_RELEASE_RESET();

    } else if (_tim == TIM4) {
        __HAL_RCC_TIM4_CLK_ENABLE();
        HAL_NVIC_EnableIRQ(TIM4_IRQn);
        __HAL_RCC_TIM4_FORCE_RESET();
        __HAL_RCC_TIM4_RELEASE_RESET();

#if 0
    } else if (_tim == TIM5) {
        __HAL_RCC_TIM5_CLK_ENABLE();
        HAL_NVIC_EnableIRQ(TIM5_IRQn);
        __HAL_RCC_TIM5_FORCE_RESET();
        __HAL_RCC_TIM5_RELEASE_RESET();
#endif
    }

    /* Calculate the prescaler from the target frequency.
     *
     * APB1 clock is PCLK1 in the arduino HAL */
    uint32_t apb1_freq = HAL_RCC_GetPCLK1Freq();
    uint32_t prescaler = (apb1_freq * 2) / freq;
    LL_TIM_SetPrescaler(_tim, prescaler);

    /* Mode setting stuff to turn this into hardware driven timer interrupt */
    LL_TIM_SetOnePulseMode(_tim, LL_TIM_ONEPULSEMODE_SINGLE);
    LL_TIM_EnableARRPreload(_tim);
    LL_TIM_OC_EnablePreload(_tim, LL_TIM_CHANNEL_CH1);
    LL_TIM_OC_SetMode(_tim, LL_TIM_CHANNEL_CH1, LL_TIM_OCMODE_FROZEN);

    /* preload target value */
    LL_TIM_SetAutoReload(_tim, period);

    /* Initial target value */
    LL_TIM_OC_SetCompareCH1(_tim, period);

    /* Last, save the callback function. */
    isrCallbacks[_idx] = callback;

    /* Ensure that this timer is not running. */
    stop();
}

void OneShotHardwareTimer::stop(void) {
    LL_TIM_DisableIT_UPDATE(_tim);
    LL_TIM_DisableCounter(_tim);
}

void OneShotHardwareTimer::start(void) {
    LL_TIM_EnableCounter(_tim);
    LL_TIM_EnableIT_UPDATE(_tim);
}

void OneShotHardwareTimer::restart(void) {
    LL_TIM_SetCounter(_tim, 0);
    start();
}
