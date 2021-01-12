#include "J1708Serial.h"

/* Initialize the static class member objects now */
bool                 J1708Serial::_txAvail = true;
serial_t            *J1708Serial::_serialPtr = NULL;

Queue<J1708Msg>      J1708Serial::_rxMsgs(J1708_MSG_QUEUE_DEPTH);
Queue<J1708Msg>      J1708Serial::_txMsgs(J1708_MSG_QUEUE_DEPTH);

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

/* Some internal utility functions. */

static int utility_available(serial_t *obj) {
    return ((unsigned int)(SERIAL_RX_BUFFER_SIZE + obj->rx_head - obj->rx_tail)) % SERIAL_RX_BUFFER_SIZE;
}

static int utility_read(serial_t *obj) {
    /* if the head isn't ahead of the tail, we don't have any characters */
    if (obj->rx_head == obj->rx_tail) {
        return -1;
    } else {
        unsigned char c = obj->rx_buff[obj->rx_tail];
        obj->rx_tail = (rx_buffer_index_t)(obj->rx_tail + 1) % SERIAL_RX_BUFFER_SIZE;
        return c;
    }
}

void J1708Serial::begin(void) {
    /* Configure the J1708 message timers */
    configure();

    /* Now duplicate the important parts of HardwareSerial::begin() but 
     * using the J1708 specified values, and using the rx callback function 
     * for this class. */
    uart_init(&_serial, J1708_BAUD, J1708_NUMBITS, J1708_PARITY, J1708_STOPBITS);
    uart_attach_rx_callback(&_serial, J1708Serial::_rx_complete_irq);
}

void J1708Serial::configure(void) {
    /* Initialize the timers */
    _EOMTimer.configure(TIMER_FREQ,
                        J1708_MSG_TIMEOUT * TIMER_TICKS_PER_BIT,
                        _eomCallback);

    _COLTimer.configure(TIMER_FREQ,
                        J1708_DEFAULT_COLLISION_WAIT * TIMER_TICKS_PER_BIT,
                        _colCallback);
}

bool J1708Serial::_isTxAllowed(void) {
    /* Transmit can happen if the Tx Collision wait timer is not running and 
     * there is not a message currently being received. */
    return _txAvail && available() == 0;
}

void J1708Serial::_handleTxCollision(void) {
    _txAvail = false;
    _COLTimer.restart();
}

bool J1708Serial::msgAvailable(void) {
    return !_rxMsgs.isEmpty();
}

bool J1708Serial::msgRecv(J1708Msg *msg) {
    if (msgAvailable()) {
        /* First see if there are any messages that have already been received, 
         * if so we should receive them first. */
        *msg = _rxMsgs.dequeue();
        return true;
    } else if (!_txMsgs.isEmpty()) {
        /* If no messages have been received see if there are any messages 
         * waiting to be sent */
        J1708Msg txMsg = _txMsgs.peek();

        /* Check if we can transmit or not, if not we will return false 
         * indicating that the message was not sent. */
        if (_isTxAllowed()) {
            /* Now send the message */
            for (int i = 0; i < txMsg.len; i++) {
                write(txMsg.buf[i]);
            }

            /* Now wait until the next message is received */
            while (!msgAvailable());
            *msg = _rxMsgs.dequeue();

            /* Check if the new message matches the message we just sent. */
            if (0 == memcmp(&txMsg, msg, sizeof(J1708Msg))) {
                /* the message was successfully transmitted, remove it from the 
                 * Tx queue and return the readback message as one that was just 
                 * received. */
                _txMsgs.remove();
                return true;
            } else {
                _handleTxCollision();

                /* If transmit failed, the received message is not valid so 
                 * discard it */
                return false;
            }
        } /* if (_isTxAllowed()) */
    } /* else if (!_txMsgs.isEmpty()) */

    /* No message has been received. */
    return false;
}

void J1708Serial::msgSend(J1708Msg msg) {
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
    int32_t avail = utility_available(J1708Serial::_serialPtr);

    /* Regardless of whether this message will be considered "valid" or not, 
     * read all the available characters into our temp msg buffer. */
    for (int i = 0; i < SERIAL_RX_BUFFER_SIZE; i++) {
        tempBuf[i] = utility_read(J1708Serial::_serialPtr);
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

/* Virtual functions that are just a pass through to the parent class */
int J1708Serial::available(void) {
    return utility_available(&_serial);
}

int J1708Serial::peek(void) {
    if (_serial.rx_head == _serial.rx_tail) {
        return -1;
    } else {
        return _serial.rx_buff[_serial.rx_tail];
    }
}

int J1708Serial::read(void) {
    return utility_read(&_serial);
}

void J1708Serial::flush(void) {
    /* Wait until the Tx buffer is cleared by the Tx interrupt handler */
    while (_written && (_serial.tx_head != _serial.tx_tail));
}

size_t J1708Serial::write(uint8_t c) {
    _written = true;

    tx_buffer_index_t i = (_serial.tx_head + 1) % SERIAL_TX_BUFFER_SIZE;

    /* Wait until the Tx buffer is not full */
    while (i == _serial.tx_tail);

    _serial.tx_buff[_serial.tx_head] = c;
    _serial.tx_head = i;

    if (!serial_tx_active(&_serial)) {
        uart_attach_tx_callback(&_serial, _tx_complete_irq);
    }

    return 1;
}
