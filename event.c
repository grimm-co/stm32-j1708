
#include <libopencm3/cm3/cortex.h>
#include "event.h"

void event_init(event_t *event) {
    CM_ATOMIC_CONTEXT();
    event->set = 0;
    event->value = 0;
}

int32_t event_wait(event_t *event) {
    int32_t value;
    uint32_t set = 0;

    while (set != 0) {
        CM_ATOMIC_CONTEXT();
        set = event->set;
    }
    value = event->value;

    return value;
}

int32_t event_nowait(event_t *event) {
    CM_ATOMIC_CONTEXT();
    return event->value;
}

void event_signal(event_t *event, int32_t value) {
    CM_ATOMIC_CONTEXT();
    event->value = value;
    event->set = 1;
}

void event_putvalue(event_t *event, int32_t value) {
    /* Atomically set the value , but don't signal the event. */
    CM_ATOMIC_CONTEXT();
    event->value = value;
}

