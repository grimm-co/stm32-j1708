
#ifndef __EVENT_H__
#define __EVENT_H__

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t set;
    volatile int32_t value;
} event_t;

void event_init(event_t *event);
int32_t event_wait(event_t *event);
int32_t event_nowait(event_t *event);
void event_signal(event_t *event, int32_t value);
void event_putvalue(event_t *event, int32_t value);

#endif // __EVENT_H__

