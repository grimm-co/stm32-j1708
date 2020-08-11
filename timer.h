#ifndef __TIMER_H__
#define __TIMER_H__

/* Mapping the J1708 events we use timers for to the STM32 timer names */
#define EOM_TIMER TIM2
#define COL_TIMER TIM3

typedef void (*timer_handler_t)(void);

void timer_setup(void);
void timer_set_handler(uint32_t timer_peripheral, timer_handler_t handler);
void timer_start(uint32_t timer_peripheral);
void timer_stop(uint32_t timer_peripheral);
void timer_restart(uint32_t timer_peripheral);

#endif // __TIMER_H__
