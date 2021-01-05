
//#include <libopencm3/cm3/cortex.h>
#include "event.h"

void event_init(event_t *event) {
    event->lock = MUTEX_UNLOCKED;
    event->set = false;
    event->value = 0;
}

void event_clear(event_t *event) {
    mutex_lock(&event->lock);
    event->set = false;
    event->value = 0;
    mutex_unlock(&event->lock);
}

int32_t event_wait(event_t *event) {
    int32_t value;
    bool set;

    do {
        mutex_lock(&event->lock);
        set = event->set;
        value = event->value;
        mutex_unlock(&event->lock);
    } while (!set);

    return value;
}

bool event_isset(event_t *event) {
    bool set;

    mutex_lock(&event->lock);
    set = event->set;
    mutex_unlock(&event->lock);

    return set;
}

void event_signal(event_t *event, int32_t value) {
    mutex_lock(&event->lock);
    event->set = true;
    event->value = value;
    mutex_unlock(&event->lock);
}

void event_putvalue(event_t *event, int32_t value) {
    /* Change the value , but don't signal the event. */
    mutex_lock(&event->lock);
    event->value = value;
    mutex_unlock(&event->lock);
}

