#include "OneShotHardwareTimer.h"

OneShotHardwareTimer::OneShotHardwareTimer(TIM_TypeDef *instance) :
    HardwareTimer(instance)
{}

OneShotHardwareTimer::~OneShotHardwareTimer() {
    // Nothing special to do
}

void OneShotHardwareTimer::restart(void) {
    HardwareTimer::setCount(0, TICK_FORMAT);
    HardwareTimer::resume();
}

void OneShotHardwareTimer::setOneShotMode(bool value) {
    TIM_HandleTypeDef *handle = getHandle();
    uint32_t mode = value ? LL_TIM_ONEPULSEMODE_SINGLE : LL_TIM_ONEPULSEMODE_REPETITIVE;

    LL_TIM_SetOnePulseMode(handle->Instance, mode);
}

bool OneShotHardwareTimer::getOneShotMode(void) {
    TIM_HandleTypeDef *handle = getHandle();
    uint32_t mode = LL_TIM_GetOnePulseMode(handle->Instance);

    return mode == LL_TIM_ONEPULSEMODE_SINGLE;
}
