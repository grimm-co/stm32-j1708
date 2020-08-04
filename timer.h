#ifndef __TIMER_H__
#define __TIMER_H__

typedef void (*timer_handler_t)(uint32_t counter_val);

void timer_setup(void);
void timer_config(timer_handler_t handler, uint16_t freq);
void timer_start(uint32_t count);
void timer_stop(void);

#endif // __TIMER_H__
