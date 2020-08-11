
#include "main.h"
#include "j1708.h"
#include "usb.h"
#include "msg.h"

static void clock_setup(void) {
    rcc_clock_setup_in_hse_8mhz_out_72mhz();
}

int main(void) {
    msg_t msg;

    clock_setup();
    j1708_setup();
    usb_setup();

    while (1) {
        if (j1708_msg_avail()) {
            /* Transfer any message received from the J1708 UART to the host */
            msg.len = j1708_read((uint8_t*) msg.buf);
            j1708_to_host(&msg);
        }
        if (usb_connected() && usb_msg_avail()) {
            /* Send any valid message received from the host to J1708 */
            msg.len = usb_read((uint8_t*) msg.buf);
            host_to_j1708(&msg);
        }
    }

    return 0;
}

