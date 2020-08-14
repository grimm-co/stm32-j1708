
#include <stdint.h>
#include <stdbool.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/sync.h>
#include "main.h"
#include "led.h"
#include "j1708.h"
#include "usb.h"
#include "msg.h"

static void clock_setup(void) {
    rcc_clock_setup_in_hse_8mhz_out_72mhz();
}

int main(void) {
    msg_t msg;

    clock_setup();
    led_setup();
    usb_setup();
    j1708_setup();

    while (1) {
        /* If a J1708 message as been received, use the LED to indicate that 
         * a message was received and try to send it to a USB host. */
        if (j1708_read_msg(&msg)) {
            led_toggle();
            usb_write_msg(&msg);
        }

        /* If a USB host is connected, and we did receive a message, send that 
         * message received from the host to the J1708 bus. */
        if (usb_connected() && usb_read_msg(&msg)) {
            j1708_write_msg(&msg);
        }

#ifndef USB_POLL_INTERRUPTS
        usb_poll();
#endif
    }

    return 0;
}

