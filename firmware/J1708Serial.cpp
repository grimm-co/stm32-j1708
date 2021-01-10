#include "J1708Serial.h"
#include "led.h"

/* Initialize the static class member objects now */
bool                 J1708Serial::_txAvail = true;

HardwareSerial      *J1708Serial::_hwDev = NULL;
serial_t            *J1708Serial::_serial = NULL;

Queue<J1708Msg>     J1708Serial::_rxMsgs(J1708_MSG_QUEUE_DEPTH);
Queue<J1708Msg>     J1708Serial::_txMsgs(J1708_MSG_QUEUE_DEPTH);

OneShotHardwareTimer J1708Serial::_EOMTimer(J1708_EOM_TIMER);
OneShotHardwareTimer J1708Serial::_COLTimer(J1708_COL_TIMER);

/* The timer source is rcc_apb1_frequency * 2, we want to ensure that the 
 * prescaler allows for accurately counting 9600 baud signals and also fits 
 * within a 16-bit value, so set the frequency to be 48khz. This will count 
 * 5 per 9600 baud "bit time" */
const uint32_t TIMER_FREQ = 48000;
const uint16_t TIMER_TICKS_PER_BIT = TIMER_FREQ / J1708_BAUD;

/* According to the SAE J1708 standard the timeout for end of a message is 10 
 * "bit times" the baud rate is 9600 the timeout Hz is 9600 / 10 =  960.
 * According to my testing, we need a slightly longer timeout, perhaps the 
 * timing on the STM32 device is too precise?  Or perhaps I a measuring from the 
 * wrong point. */
const uint16_t J1708_MSG_TIMEOUT = 10 + 1;

/* The priority idle time (when a tx collision occurs).  The transmit retry 
 * delay time is defiend in the J1708 standard. */
#define J1708_COLLISION_WAIT(msg_priority) (J1708_MSG_TIMEOUT + ((msg_priority) * 2))
const uint16_t J1708_DEFAULT_COLLISION_WAIT = J1708_COLLISION_WAIT(8);

void J1708Serial::configure(void) {
    /* APB1 clock is PCLK1 in the arduino HAL */
    uint32_t apb1_freq = HAL_RCC_GetPCLK1Freq();
    uint32_t timer_prescaler = (apb1_freq * 2) / TIMER_FREQ;

    /* Initialize the timers */
    _EOMTimer.setOneShotMode(true);
    _EOMTimer.setPrescaleFactor(timer_prescaler);
    _EOMTimer.setPreloadEnable(true);
    _EOMTimer.setMode(TIM_CHANNEL_1, TIMER_OUTPUT_COMPARE, NC);
    _EOMTimer.setOverflow(J1708_MSG_TIMEOUT * TIMER_TICKS_PER_BIT);
    _EOMTimer.attachInterrupt(_eomCallback);

    _COLTimer.setOneShotMode(true);
    _COLTimer.setPrescaleFactor(timer_prescaler);
    _COLTimer.setPreloadEnable(true);
    _COLTimer.setMode(TIM_CHANNEL_1, TIMER_OUTPUT_COMPARE, NC);
    _COLTimer.setOverflow(J1708_DEFAULT_COLLISION_WAIT * TIMER_TICKS_PER_BIT);
    _COLTimer.attachInterrupt(_colCallback);
}

bool J1708Serial::_isTxAllowed(void) {
    /* Transmit can happen if the Tx Collision wait timer is not running and 
     * there is not a message currently being received. */
    return _txAvail && _hwDev->available() == 0;
}

void J1708Serial::_handleTxCollision(void) {
    noInterrupts();
    _txAvail = false;
    interrupts();

    _EOMTimer.restart();
}

bool J1708Serial::_sendMsg(J1708Msg msg) {
    J1708Msg incomingMsg;

    /* Check if we can transmit or not, if not we will return false indicating 
     * that the message was not sent. */
    if (!_isTxAllowed()) {
        return false;
    }

    /* Now send the message */
    for (int i = 0; i < msg.len; i++) {
        _hwDev->write(msg.buf[i]);
    }

    /* Now wait until the next message is received */
    while (_rxMsgs.isEmpty());
    incomingMsg = _rxMsgs.dequeue();

    /* Check if the new message matches the message we just sent.  If so, 
     * the message was successfully transmitted, if not ...*/
    if (0 == memcmp(&msg, &incomingMsg, sizeof(J1708Msg))) {
        return true;
    } else {
        _handleTxCollision();
        return false;
    }
}

J1708Msg J1708Serial::_getMsg(void) {
    /* Return any received message that may be in the queue, If nothing is 
     * present this will just return NULL */
    return _rxMsgs.dequeue();
}

bool J1708Serial::available(void) {
    return _rxMsgs.isEmpty();
}

J1708Msg J1708Serial::read(void) {
    /* First see if there are any messages waiting to be sent */
    if (!_txMsgs.isEmpty()) {
        J1708Msg tmp = _txMsgs.peek();
        if (_sendMsg(tmp)) {
            /* If the message was sent successfully remove the transmitted 
             * message from the queue */
            _txMsgs.remove();
        }
    }

    return _getMsg();
}

void J1708Serial::write(J1708Msg msg) {
    /* Just enqueue the new message to be sent
     * TODO: may need to make this smarter eventually and squash duplicates
     *       based on source MID or something */

    if (!_txMsgs.enqueue(&msg)) {
        /* If the message failed to enqueue, the queue is full. Discard the 
         * oldest item. */
        _txMsgs.remove();
        _txMsgs.enqueue(&msg);
    }
}

void J1708Serial::_rx_complete_irq(serial_t *obj) {
    unsigned char c;

    if (uart_getc(obj, &c) == 0) {

        rx_buffer_index_t i = (unsigned int)(obj->rx_head + 1) % SERIAL_RX_BUFFER_SIZE;
        if (i != obj->rx_tail) {
            obj->rx_buff[obj->rx_head] = c;
            obj->rx_head = i;
        }

        /* *** New for J1708Serial class ***
         * Most of this function is a duplicate of the HardwareSerial function, 
         * to support J1708 we need to identify when messages are complete, the 
         * way to do that is to start a timer when each character is received 
         * and when the timer expires take the received characters and save them 
         * as a message. */
        _EOMTimer.restart();
    }
}

void J1708Serial::_eomCallback(void) {
    /* Use a temp buffer for the message in case there are more characters than 
     * expected. */
    uint8_t tempBuf[SERIAL_RX_BUFFER_SIZE];
    int32_t avail = _hwDev->available();

    /* Regardless of whether this message will be considered "valid" or not, 
     * read all the available characters into our temp msg buffer. */
    for (int i = 0; i < SERIAL_RX_BUFFER_SIZE; i++) {
        tempBuf[i] = _hwDev->read();
    }

    /* If the message is >= the MIN size and <= the MAX size, it is valid so add 
     * it to the queue. */
    if ((avail >= J1708_MSG_MIN_SIZE) && (avail <= J1708_MSG_MAX_SIZE)) {
        J1708Msg msg;
        memcpy(msg.buf, tempBuf, avail);
        msg.len = avail;
        _rxMsgs.enqueue(&msg);

        /* A message was successfully received, toggle the led */
        led_toggle();
    }
}

void J1708Serial::_colCallback(void) {
    /* Transmitting can resume */
    _txAvail = true;
}
