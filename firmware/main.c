
#include <stdint.h>
#include <stdbool.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/sync.h>
#include "main.h"
#include "j1708.h"
#include "usb.h"
#include "msg.h"
#include "systick.h"

static void clock_setup(void) {
    //rcc_clock_setup_in_hse_8mhz_out_72mhz();
    rcc_clock_setup_pll(&rcc_hse_configs[RCC_CLOCK_HSE8_72MHZ]);
}

int main(void) {
    msg_t msg, host_msg;

    clock_setup();
    /* systick isn't really used, could probably remove it */
    systick_setup();
    j1708_setup();
    usb_setup();

    while (1) {
        if (usb_connected()) {
            if (usb_read_msg(&host_msg)) {
                if (from_host_msg(&msg, &host_msg)) {
                    j1708_write_msg(&msg);
                }
            } 
            if (j1708_read_msg(&msg)) {
                to_host_msg(&host_msg, &msg);
                usb_write_msg(&host_msg);
            }
        }
    }

    return 0;
}

