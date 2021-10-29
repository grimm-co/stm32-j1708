#include "J1708Serial.h"

/* TODO: These could be class static variables */
static bool                 _txAvail = false;
static serial_t            *_serialPtr = NULL;

static Queue<J1708Msg>      _rxMsgs(J1708_MSG_QUEUE_DEPTH);
static Queue<J1708Msg>      _txMsgs(J1708_MSG_QUEUE_DEPTH);

static OneShotHardwareTimer _EOMTimer(J1708_EOM_TIMER);
static OneShotHardwareTimer _COLTimer(J1708_COL_TIMER);

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
    /* Simplified availability calculation because J1708 operates on "messages"
     * which should never exceed the receive buffer size. */
    return obj->rx_head - obj->rx_tail;
}

J1708Serial::J1708Serial(int _tx, int _rx) :
    HardwareSerial(_tx, _rx)
{}

void J1708Serial::begin(void) {
    /* Configure the J1708 message timers */
    configure();

    /* Now duplicate the important parts of HardwareSerial::begin() but
     * using the J1708 specified values, and using the rx callback function
     * for this class. */
    uart_init(&_serial, J1708_BAUD, J1708_NUMBITS, J1708_PARITY, J1708_STOPBITS);
    uart_attach_rx_callback(&_serial, _rx_complete_irq);
}

void J1708Serial::configure(void) {
    /* Transmit is allowed now. */
    _txAvail = true;

    /* Save the _serial object to our static pointer variable to let the
     * callbacks access the serial object. */
    _serialPtr = &_serial;

    /* Initialize the timers */
    _EOMTimer.configure(TIMER_FREQ,
                        J1708_MSG_TIMEOUT * TIMER_TICKS_PER_BIT,
                        J1708Serial::_eomCallback);

    _COLTimer.configure(TIMER_FREQ,
                        J1708_DEFAULT_COLLISION_WAIT * TIMER_TICKS_PER_BIT,
                        J1708Serial::_colCallback);
}

bool J1708Serial::_isTxAllowed(void) {
    /* Transmit can happen if another message is not currently transmitting, the
     * Tx Collision wait timer is not running, and there is not a message
     * currently being received. */
    return !_transmitting() && _txAvail && !available();
}

bool J1708Serial::_transmitting(void) {
    /* We can determine if a message is being transmitted by if tx_tail is not
     * 0 and tx_tail == tx_head. */
    return ((_serial.tx_tail != 0) && (_serial.tx_head != _serial.tx_tail));
}

void J1708Serial::_handleTxCollision(void) {
    _txAvail = false;
    _COLTimer.restart();
}

bool J1708Serial::msgAvailable(void) {
    return !_rxMsgs.isEmpty();
}

bool J1708Serial::_checkTxSuccess(J1708Msg *msg) {
#ifdef J1708_NO_TX_VALIDATE
    return false;
#else
    /* Now wait until the next message is received */
    while (!msgAvailable());
    *msg = _rxMsgs.dequeue();

#ifdef J1708_RX_DEBUG
    SerialUSB.print("Comparing: ");
    for (int i = 0; i < msg->len; i++) {
        SerialUSB.print(msg->buf[i], HEX);
    }
    SerialUSB.println();
#endif

    /* Check if the new message matches the message we just sent.
     * tx_head indicates the size of the message that was sent. */
    if ((_serial.tx_head == msg->len)
        && (0 == memcmp(_serial.tx_buff, msg->buf, msg->len))) {
#ifdef J1708_RX_DEBUG
        SerialUSB.println("Match");
#endif
        /* the message was successfully transmitted, Reset tx_tail and
         * tx_head to 0 to indicate that the message has been
         * validated. */
        _serial.tx_tail = 0;
        _serial.tx_head = 0;
        return true;
    } else {
#ifdef J1708_RX_DEBUG
        SerialUSB.println("No match");
#endif
        /* Set tx_tail back to 0, but leave tx_head as-is.  This
         * indicates that the message we attempted to send did not fully
         * validate and needs to be re-tried, but the tx_head value will
         * maintain the length of the message being sent. */
        _serial.tx_tail = 0;

        _handleTxCollision();

        /* If transmit failed, the received message is not valid so
         * discard it */
        return false;
    }
#endif
}

bool J1708Serial::msgRecv(J1708Msg *msg) {
    if (msgAvailable()) {
        /* First see if there are any messages that have already been received,
         * if so we should receive them first. */
        *msg = _rxMsgs.dequeue();

#ifdef J1708_RX_DEBUG
        SerialUSB.print("Received: ");
        for (int i = 0; i < msg->len; i++) {
            SerialUSB.print(msg->buf[i], HEX);
        }
        SerialUSB.println();
#endif

        return true;
    }

    /* If no messages have been received see if there are any messages waiting
     * to be sent */
    if (_isTxAllowed() && !serial_tx_active(&_serial)) {
        /* Is there a message that we tried to send but it failed and needs to
         * be retried?  If not check if there are any new messages that need to
         * be sent. */
        if ((_serial.tx_tail == 0) && (_serial.tx_head != 0)) {
            /* try again, tx_head has not been modified so there is nothing that
             * needs to be done except call the HAL Tx function */
#ifdef J1708_TX_DEBUG
            SerialUSB.print("Resending: ");
            for (int i = 0; i < _serial.tx_head; i++) {
                SerialUSB.print(_serial.tx_buff[i], HEX);
            }
            SerialUSB.println();
#endif
            /* The STM32 UART driver (uart_attach_tx_callback) has been updated
             * to allow sending more than 1 byte at a time, but we know the 1
             * byte at a time method works, and allows detecting collisions so
             * just use a size of 1. */
            uart_attach_tx_callback(&_serial, J1708Serial::_tx_complete_irq, 1);
            return _checkTxSuccess(msg);

        } else if (!_txMsgs.isEmpty() ) {
            /* Dequeue the message to be sent. */
            J1708Msg txMsg = _txMsgs.dequeue();

#ifdef J1708_TX_DEBUG
            SerialUSB.print("Sending: ");
            for (int i = 0; i < txMsg.len; i++) {
                SerialUSB.print(txMsg.buf[i], HEX);
            }
            SerialUSB.println();
#endif

            /* Copy this message into the _tx_buffer */
            memcpy(_serial.tx_buff, txMsg.buf, txMsg.len);

            /* For mysterious reasons the STM32 UART HAL uses head to point to
             * the newest data to send (end of a message) and tail to point to
             * the oldest data to send (start of a message).  This is confusing
             * and weird, but whatever. */
            _serial.tx_tail = 0;
            _serial.tx_head = txMsg.len;
            uart_attach_tx_callback(&_serial, J1708Serial::_tx_complete_irq, 1);
            return _checkTxSuccess(msg);
        }
    } /* if (_isTxAllowed() && !serial_tx_active(_serial)) */

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

        uint16_t i = (obj->rx_head + 1) % SERIAL_RX_BUFFER_SIZE;
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

int J1708Serial::_tx_complete_irq(serial_t *obj) {
    /* The STM32 UART HAL uses the serial_t object to keep track of transmit and
     * receive data. For whatever reason it uses a tail and head pointer with
     * the tail indicating the start of the message and the head indicating the
     * end of the message.
     *
     * This callback is used to walk through the bytes that need to be sent so
     * increment the tx_tail until it is the same as tx_head.  No need to mod
     * the tx_tail by SERIAL_TX_BUFFER_SIZE like the HardwareSerial class does
     * because J1708 messages will never exceed SERIAL_TX_BUFFER_SIZE */
    obj->tx_tail++;

    if (obj->tx_head == obj->tx_tail) {
        /* Message has been sent, Leave the tx_tail as-is to indicate that this
         * message has been transmitted but requires validation. */
#ifdef J1708_NO_TX_VALIDATE
        obj->tx_head = 0;
        obj->tx_tail = 0;
        led_toggle();
#endif

        return -1;
    } else {
        /* Returning 0 indicates "success" (there are more bytes to be sent) */
        return 0;
    }
}

void J1708Serial::_eomCallback(void) {
    int32_t avail = utility_available(_serialPtr);

    /* If the message is >= the MIN size and <= the MAX size, it is valid so add
     * it to the queue. */
    if ((avail >= J1708_MSG_MIN_SIZE) && (avail <= J1708_MSG_MAX_SIZE)) {
        /* For reasons I don't understand the "rx_tail" points to the oldest
         * character and the "rx_head" points to the newest.  So copy from tail
         * to head.
         *
         * But because we are reading messages from start to end the tail should
         * always point to index 0. */
        J1708Msg msg;
        memcpy(msg.buf, _serialPtr->rx_buff, avail);
        msg.len = avail;
        _rxMsgs.enqueue(&msg);

        /* Reset head and tail back to 0 just to make life easier in the
         * future. */
        _serialPtr->rx_tail = 0;
        _serialPtr->rx_head = 0;

#ifndef J1708_NO_TX_VALIDATE
        /* A message was successfully received, toggle the led */
        led_toggle();
#endif
    }
}

void J1708Serial::_colCallback(void) {
    /* Transmitting can resume */
    _txAvail = true;

    /* TODO: In theory we could initiate a transmit from here but that makes the
     * normal send/receive processing loop more complicated, and it probably
     * doesn't get us any benefit. So for now just  change the flag. */
}

/* Virtual functions that are just a pass through to the parent class */
int J1708Serial::available(void) {
    return utility_available(&_serial);
}

int J1708Serial::peek(void) {
    /* This function is defined as virtual in the HardwareSerial class so we
     * have to define it, but we aren't going to use this for the J1708Serial
     * class so it is empty. */
    return -1;
}

int J1708Serial::read(void) {
    /* This function is defined as virtual in the HardwareSerial class so we
     * have to define it, but we aren't going to use this for the J1708Serial
     * class so it is empty. */
    return -1;
}

void J1708Serial::flush(void) {
    /* This function is defined as virtual in the HardwareSerial class so we
     * have to define it, but we aren't going to use this for the J1708Serial
     * class so it is empty. */
}

size_t J1708Serial::write(uint8_t c) {
    /* This function is defined as virtual in the HardwareSerial class so we
     * have to define it, but we aren't going to use this for the J1708Serial
     * class so it is empty. */
    return 0;
}
