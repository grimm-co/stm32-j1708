#ifndef __SYSTICK_H__
#define __SYSTICK_H__

#include <stdint.h>

void systick_setup(void);
void systick_msleep(uint32_t delay);
uint32_t systick_gettime(void);

#endif // __SYSTICK_H__
