
#include <string.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/timer.h>
#include <libopencm3/cm3/nvic.h>
#include <libopencm3/cm3/sync.h>
#include "j1708.h"
#include "timer.h"

#define J1708_UART USART1

static msg_queue_t j1708_rx_queue;
static msg_queue_t j1708_tx_queue;
static volatile msg_t rx_msg;
static volatile msg_t tx_msg;
static volatile uint32_t tx_idx;

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

    usart_enable_rx_interrupt(J1708_UART);

    usart_enable(J1708_UART);
}

static inline void enable_tx(void) {
    USART_CR1(J1708_UART) |= USART_CR1_TXEIE | USART_CR1_TCIE;
}

static inline void disable_tx(void) {
    USART_CR1(J1708_UART) &= ~(USART_CR1_TXEIE | USART_CR1_TCIE);
}

static inline bool tx_in_progress(void) {
    return tx_msg.len != 0;
}

static inline bool rx_in_progress(void) {
    return rx_msg.len != 0;
}

static bool j1708_tx_next_msg(void) {
    /* Reset the tx message index. This can be done regardless of if there is 
     * a new message pending because this function is only called when a new 
     * message transmit should begin.*/
    tx_idx = 0;

    /* If there is a tx message queued up, copy it into the tx_msg buffer. */
    if (msg_pop(&j1708_tx_queue, (msg_t*) &tx_msg)) {

        /* Enable the Tx interrupts and transmit the first byte, this will kick 
         * off the message transmission. */
        //usart_send(J1708_UART, tx_msg.buf[0]);
        USART_DR(J1708_UART) = (uint16_t) tx_msg.buf[0];
        enable_tx();
    } else {
        /* There is no new message to send, so set the tx_msg length to 0 to 
         * indicate Tx is not in progress. */
        tx_msg.len = 0;
    }

    return tx_in_progress();
}

static void j1708_eom_timer_handler(void) {
    /* If a J1708 message was being received it is complete, save it */
    if (rx_in_progress()) {
        msg_push(&j1708_rx_queue, (msg_t*) &rx_msg);

        /* Reset the receive in-progress buffer */
        rx_msg.len = 0;
    }

    /* There may be a transmit message that was delayed due to the incoming 
     * message, start message tx now if one is pending. */
    j1708_tx_next_msg();
}

static void j1708_col_timer_handler(void) {
    j1708_tx_next_msg();
}

void j1708_setup(void) {
    msg_queue_init(&j1708_rx_queue);
    msg_queue_init(&j1708_tx_queue);
    msg_init((msg_t*) &rx_msg);
    msg_init((msg_t*) &tx_msg);

    timer_set_handler(EOM_TIMER, j1708_eom_timer_handler);
    timer_set_handler(COL_TIMER, j1708_col_timer_handler);

    timer_setup();
    usart_setup();

    //DEBUG
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO1);
    gpio_clear(GPIOA, GPIO1);
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO3);
    gpio_clear(GPIOA, GPIO3);
}

bool j1708_msg_avail(void) {
    return msg_avail(&j1708_rx_queue);
}

bool j1708_read_msg(msg_t *msg) {
    return msg_pop(&j1708_rx_queue, msg);
}

void j1708_write_msg(msg_t *msg) {
    /* Queue up the message to be sent. */
    msg_push(&j1708_tx_queue, msg);

    /* If Rx or Tx is currently in progress then do nothing, the next message to 
     * transmit will get started after the current operation is complete. */
    if (!tx_in_progress() && !rx_in_progress()) {
        /* No need to check the return value of this function, we know there is 
         * at least one message in the queue. */
        j1708_tx_next_msg();
    }
}

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

static void handle_tx_collision(void) {
    uint32_t pri;

    /* Disable Tx */
    disable_tx();

    /* Reset the tx index */
    tx_idx = 0;

    /* Configure the collision wait timer delay based on the priority of the 
     * message. */
    pri = j1708_msg_priority((msg_t*) &tx_msg);
    timer_set_wait(TIM2, J1708_COLLISION_WAIT(pri));
    timer_start(COL_TIMER);
}

void usart1_isr(void) {
    uint8_t data;
    uint32_t cr1, sr;

    cr1 = USART_CR1(J1708_UART);
    sr = USART_SR(J1708_UART);

    if ((cr1 & USART_CR1_RXNEIE) && (sr & USART_SR_RXNE)) {
        gpio_toggle(GPIOA, GPIO1);
        /* Retrieve the byte from the peripheral. */
        data = (uint8_t) usart_recv(J1708_UART);

        if (tx_in_progress()) {
            /* If the byte we just received does not match what we attempted to 
             * send, a collision occurred, stop the Tx interrupt and start the 
             * collision retry timer. */
            if (data != tx_msg.buf[tx_idx]) {
                handle_tx_collision();
            }
        } else {
            /* If a transmission is not happening, save the data on the current 
             * message and restart the end of message timer. */
            rx_msg.buf[rx_msg.len] = data;
            rx_msg.len++;
            timer_restart(EOM_TIMER);
        }
    }

    if ((cr1 & USART_CR1_TXEIE) && (sr & USART_SR_TXE)) {
        //DEBUG
        gpio_toggle(GPIOA, GPIO3);

        /* Increment the tx_msg index and send the next byte.  The index is 
         * incremented here so that when the received data is validated against 
         * the transmitted data the tx_idx points to the data last txd. */
        tx_idx++;

        if (tx_idx < tx_msg.len) {
            USART_DR(J1708_UART) = (uint16_t) tx_msg.buf[tx_idx];
        } else {
            /* Disable the TXE interrupt, we don't need it anymore */
            USART_CR1(J1708_UART) &= ~USART_CR1_TXEIE;
        }
    }

    if ((cr1 & USART_CR1_TCIE) && (sr & USART_SR_TC)) {
        /* Message send is complete, before sending another message we should 
         * ensure that EOM time elapses. */
        disable_tx();
        timer_restart(EOM_TIMER);
    }
}
