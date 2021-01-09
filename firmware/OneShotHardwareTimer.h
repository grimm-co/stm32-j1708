#ifndef __ONESHOTHARDWARETIMER_H__
#define __ONESHOTHARDWARETIMER_H__

#include <HardwareTimer.h>

class OneShotHardwareTimer : public HardwareTimer {
    public:
        OneShotHardwareTimer(TIM_TypeDef *instance);
        ~OneShotHardwareTimer();

        void restart(void);
        void setOneShotMode(bool value);
        bool getOneShotMode(void);
};

#endif /* __ONESHOTHARDWARETIMER_H__ */
