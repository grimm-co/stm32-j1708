#ifndef __ONESHOTHARDWARETIMER_H__
#define __ONESHOTHARDWARETIMER_H__

#include <Arduino.h>

extern "C" {
    typedef enum {
        TIMER2_INDEX,
        TIMER3_INDEX,
        TIMER4_INDEX,
#if 0
        TIMER5_INDEX,
#endif
        TIMER_NUM,
        UNKNOWN_TIMER = 0xFFFF
    } timer_index_t;
}

class OneShotHardwareTimer {
    public:
        OneShotHardwareTimer(TIM_TypeDef *instance);

        void configure(uint32_t freq, uint32_t period, callback_function_t callback);
        void stop(void);
        void start(void);
        void restart(void);

    private:
        TIM_TypeDef *_tim;
        timer_index_t _idx;
};

#endif /* __ONESHOTHARDWARETIMER_H__ */
