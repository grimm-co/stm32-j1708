
#include <string.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/timer.h>
#include <libopencm3/cm3/nvic.h>
#include <libopencm3/cm3/cortex.h>
#include "main.h"
#include "j1708.h"
#include "timer.h"
#include "led.h"
#include "event.h"
#include "msg.h"

#define J1708_UART USART1

static msg_queue_t j1708_rx_queue;
static msg_t rx_msg;
static msg_t tx_msg;
static event_t msg_sent_event;

static void usart_setup(void) {
    rcc_periph_clock_enable(RCC_GPIOA);
    rcc_periph_clock_enable(RCC_AFIO);
    rcc_periph_clock_enable(RCC_USART1);

    nvic_enable_irq(NVIC_USART1_IRQ);

    /* Use the alternate output function so TX is high when idle */
    gpio_set_mode(GPIO_BANK_USART1_TX, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO_USART1_TX);
    gpio_set_mode(GPIO_BANK_USART1_RX, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO_USART1_RX);

    /* SAE J1708 is 9600 8N1 */
    usart_set_baudrate(J1708_UART, 9600);
    usart_set_databits(J1708_UART, 8);
    usart_set_stopbits(J1708_UART, USART_STOPBITS_1);
    usart_set_mode(J1708_UART, USART_MODE_TX_RX);
    usart_set_parity(J1708_UART, USART_PARITY_NONE);
    usart_set_flow_control(J1708_UART, USART_FLOWCONTROL_NONE);

    /* Enable Rx interrupts */
    usart_enable_rx_interrupt(J1708_UART);

    usart_enable(J1708_UART);
}

static void handle_tx_collision(void) {
    uint32_t pri;

    /* Indicate that a transmit error has occurred, but don't set the "msg_sent" 
     * event yet, that will happen after the collision timer expires. */
    event_putvalue(&msg_sent_event, -1);

    /* Configure the collision wait timer delay based on the priority of the 
     * message. */
    pri = j1708_msg_priority((msg_t*) &tx_msg);
    timer_set_wait(COL_TIMER, J1708_COLLISION_WAIT(pri));

    /* Clear the tx message length to allow receiving messages before the 
     * collision retry timer expires. */
    tx_msg.len = 0;
}

static void j1708_eom_timer_handler(void) {
    /* Message complete.  If there was a message being sent and this is the 
     * received copy of it, ensure that the message lengths match. */
    if (tx_msg.len > 0) {
        /* Confirm that the transmitted and received messages match */
        if ((rx_msg.len == tx_msg.len) 
            && memcmp(rx_msg.buf, tx_msg.buf, rx_msg.len) == 0) {
            /* signal that message transmission is complete. */
            event_signal(&msg_sent_event, rx_msg.len);

            /* Clear the transmit buffer length indicating that tx is 
             * complete. */
            tx_msg.len = 0;
        } else {
            /* If the lengths do not line up, indicate that a transmission error 
             * occurred. */
            handle_tx_collision();
        }
    }

    msg_push(&j1708_rx_queue, (msg_t*) &rx_msg);
    led_toggle();

    /* Reset the receive in-progress buffer */
    rx_msg.len = 0;
}

static void j1708_col_timer_handler(void) {
    /* Collision, send -1 indicating tx failure. */
    event_signal(&msg_sent_event, -1);

    /* Clear the transmit buffer length indicating that tx is 
     * complete. */
    tx_msg.len = 0;
}

void j1708_setup(void) {
    msg_queue_init(&j1708_rx_queue);
    msg_init(&rx_msg);
    msg_init(&tx_msg);

    timer_set_handler(EOM_TIMER, j1708_eom_timer_handler);
    timer_set_handler(COL_TIMER, j1708_col_timer_handler);

    led_setup();
    timer_setup();
    usart_setup();
}

bool j1708_msg_avail(void) {
    return msg_avail(&j1708_rx_queue);
}

bool j1708_read_msg(msg_t *msg) {
    return msg_pop(&j1708_rx_queue, msg);
}

static void j1708_wait_rx_complete(void) {
    bool complete = false;

    while (!complete) {
        CM_ATOMIC_CONTEXT();
        complete = !rx_msg.len;
    }
}

void j1708_write_msg(msg_t *msg) {
    uint16_t data;
    uint32_t len;

    len = msg->len;

    /* Copy the message into the tx_msg buffer so the ISR can validate that the 
     * bytes received match the sent bytes. */
    memcpy(tx_msg.buf, msg->buf, len);

    do {
        /* If a message is being received, wait until it is complete. */
        j1708_wait_rx_complete();

        /* Set the transmit message length and try to send it. */
        tx_msg.len = len;
        event_init(&msg_sent_event);
        for (uint32_t i = 0; i < len; i++) {
            data = tx_msg.buf[i];
            USART_DR(J1708_UART) = data;
            usart_wait_send_ready(J1708_UART);

            /* If there is a value set in the event already, abort the send. */
            if (event_nowait(&msg_sent_event) != 0) {
                break;
            }
        }
    } while (event_wait(&msg_sent_event) > 0);
}

#if 1
uint32_t j1708_msg_priority(UNUSED msg_t *msg) {
    /* My initial understanding of how message priority works in J1708 was 
     * wrong, it depends on the PID so for now just return the lowest priority 
     * for all messages. */
    return 8;
}
#else
uint32_t j1708_msg_priority(msg_t *msg) {
    /* The priority of a J1708 message is determined by the number of leading 
     * zeros in the message identifier (MID) which is the first byte of the 
     * message.  To do this quickly use the ARM clz instruction and then 
     * subtract 24 from the result to account for the uint8_t -> uint32_t 
     * casting. */
    uint32_t res, val = msg->buf[0];
    __asm__ volatile ("clz %0, %1" : "=r" (res) : "r" (val));

    /* Now we know the number of leading zeros for this MID, convert that to 
     * a J1708 "priority" by adding 1 to the result.  So instead of subtracting 
     * 24 and adding 1 we will just subtract 23 from the result. */
    return res - 23;
}
#endif

void usart1_isr(void) {
    uint8_t data;

    if ((USART_CR1(J1708_UART) & USART_CR1_RXNEIE) &&
        (USART_SR(J1708_UART) & USART_SR_RXNE)) {
        /* Retrieve the byte from the peripheral. */
        data = (uint8_t) (USART_DR(J1708_UART) & 0x00FF);

        /* Regardless of whether or not a transmission is happening, save this 
         * message. */
        rx_msg.buf[rx_msg.len++] = data;
        timer_restart(EOM_TIMER);

        /* Compare the receive buffer against the tx buffer, if the bytes or 
         * message lengths do not line up then signal a collision.
         *
         * Technically the J1708 standard says that only the first byte needs to 
         * be checked. The full received message will be checked after the 
         * message is complete, but check the first byte now to allow an early 
         * abort if necessary. */
        if ((tx_msg.len > 0) && (rx_msg.len == 1) && (rx_msg.buf[0] != tx_msg.buf[0])) {
            handle_tx_collision();
        }
    }
}
