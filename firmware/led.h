#ifndef __LED_H__
#define __LED_H__

#include <wiring.h>

#ifndef LED_BUILTIN
/* Should be defined in variant.h */
#define LED_BUILTIN PC13
#endif

inline void led_off(void) {
    digitalWrite(LED_BUILTIN, 1);
}

inline void led_on(void) {
    digitalWrite(LED_BUILTIN, 0);
}

inline void led_toggle(void) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
}

inline void led_setup(void) {
    pinMode(LED_BUILTIN, OUTPUT);
    led_off();
}

#endif // __LED_H__
