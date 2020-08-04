
#include <stdint.h>
#include <string.h>
#include "main.h"
#include "j1708.h"
#include "msg.h"
#include "led.h"
#include "timer.h"

static msg_t rx_complete = MSG_INIT;
static msg_t rx_in_progress = MSG_INIT;
static msg_t tx_in_progress = MSG_INIT;

static void usart_setup(void) {
    /* Enable GPIOA clock for USART1. */
    rcc_periph_clock_enable(RCC_GPIOA);

    /* Enable clocks for USART1. */
    rcc_periph_clock_enable(RCC_USART1);

    /* Set
     *  GPIO PA9 as USART1_TX
     *  GPIO PA10 as USART1_RX
     *  USART1_REMAP
     */
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO_USART1_TX);

    /* SAE J1708 is 9600 8N1 */
    usart_set_baudrate(USART1, 9600);
    usart_set_databits(USART1, 8);
    usart_set_stopbits(USART1, USART_STOPBITS_1);
    usart_set_mode(USART1, USART_MODE_TX_RX);
    usart_set_parity(USART1, USART_PARITY_NONE);
    usart_set_flow_control(USART1, USART_FLOWCONTROL_NONE);

    /* Enable USART1 Receive interrupt */
    USART_CR1(USART1) |= USART_CR1_RXNEIE;

    usart_enable(USART1);
}

static void j1708_clear_tx_buf(void) {
    tx_in_progress.len = 0;
    tx_in_progress.idx = 0;
}

static void j1708_tx_next_byte(void) {
    if (tx_in_progress.idx < tx_in_progress.len) {
        usart_send(USART1, tx_in_progress.buf[tx_in_progress.idx++]);

        /* Enable the Tx interrupt to send the rest of the message */
        USART_CR1(USART2) |= USART_CR1_TXEIE;
    } else {
        /* message is finished sending, disable Tx */
        USART_CR1(USART2) &= ~USART_CR1_TXEIE;
        j1708_clear_tx_buf();
    }

}

static void j1708_timer_isr(uint32_t counter_val) {
    if (J1708_MSG_TIMEOUT == counter_val) {
        /* The J1708 message is complete, save it */
        copy_to_msg(&rx_complete, rx_in_progress.buf, rx_in_progress.idx);

        /* Reset the receive in-progress buffer */
        rx_in_progress.idx = 0;
    } else if (J1708_COLLISION_WAIT == counter_val) {
        /* Time to try transmitting our message again, reset the index back to 
         * 0 and try again. */
        tx_in_progress.idx = 0;
        j1708_tx_next_byte();
    }
}

void j1708_setup(void) {
    led_setup();
    led_off();

    timer_setup();
    usart_setup();

    /* Set the timer to count J1708 "bit times" and install our timer ISR 
     * handler */
    timer_config(j1708_timer_isr, J1708_BAUD);
}

bool j1708_msg_avail(void) {
    /* Consider a J1708 message available if the length is not 0 */
    if (0 != rx_complete.len) {
        return true;
    } else {
        return false;
    }
}

uint8_t j1708_read(uint8_t *buf) {
    uint8_t len = copy_from_msg(buf, &rx_complete);

    /* Reset the rx_complete buffer before returning */
    rx_complete.len = 0;
    return len;
}

static bool is_tx_in_progress(void) {
    if ((0 < tx_in_progress.len) && (0 < tx_in_progress.idx)) {
        return true;
    } else {
        return false;
    }
}

void j1708_write(uint8_t *buf, uint8_t len) {
    /* Only allow sending a message if there is not one already in progress */
    while (0 != tx_in_progress.len);

    /* Also don't allow initiating a message send if there is a message 
     * currently being received. */
    while (0 != rx_in_progress.idx);

    /* Copy the message into the Tx buffer */
    memcpy((void*) tx_in_progress.buf, (void*) buf, len);
    tx_in_progress.len = len;
    tx_in_progress.idx = 0;

    /* Copy the first byte into the UART */
    j1708_tx_next_byte();
}

/* USART1 ISR */
void usart1_isr(void) {
    uint16_t data;

    if (((USART_CR1(USART1) & USART_CR1_RXNEIE) != 0) &&
        ((USART_SR(USART1) & USART_SR_RXNE) != 0)) {
        /* RX */

        /* Indicate that we got data. */
        led_toggle();

        /* Retrieve the data from the peripheral. */
        data = usart_recv(USART1);

        if (true == is_tx_in_progress()) {
            uint16_t prev_byte = (uint16_t) rx_in_progress.buf[rx_in_progress.idx - 1];
            /* If the byte we just received does not match what we attempted to 
             * send, a collision occurred, stop the Tx interrupt and start the 
             * collision retry timer. */
            if (prev_byte != data) {
                USART_CR1(USART2) &= ~USART_CR1_TXEIE;
                timer_start(J1708_COLLISION_WAIT);
            }
        } else {
            /* If a transmission is not happening, save the data on the current 
             * message and start/restart the end of message timer. */
            rx_in_progress.buf[rx_in_progress.idx] = (uint8_t) data;
            rx_in_progress.idx++;
            timer_start(J1708_MSG_TIMEOUT);
        }
    } else if (((USART_CR1(USART1) & USART_CR1_TCIE) != 0) &&
        ((USART_SR(USART1) & USART_SR_TC) != 0)) {
        /* TX */

        /* Send the next byte, if this function detects that the message is 
         * completely sent then the Tx interrupt will be disabled */
        j1708_tx_next_byte();
    }
}
