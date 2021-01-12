#include "J1708Serial.h"
#include "OneShotHardwareTimer.h"
#include "led.h"

/* Start/end message delimiters */
const char HOST_MSG_START = '$';
const char HOST_MSG_END   = '*';

/* The host messages are sent in printed hex so there are 2x as many characters 
 * for host messages as the max J1708 message. Also 2 characters are needed for 
 * the start/end of message delimiters. */
const uint32_t HOST_MSG_MIN_SIZE = (J1708_MSG_MIN_SIZE * 2) + 2;

/* Add one more character to the max msg size for a \0 terminator in case we 
 * want to print from this buffer. */
const uint32_t HOST_MSG_MAX_SIZE = (J1708_MSG_MAX_SIZE * 2) + 3;

/* Max msg bytes * 2 (so they can be turned into ascii), + 2 for start/end of 
 * message delimiters + 1 for NULL char */
const uint32_t HOST_MSG_BUF_SIZE = HOST_MSG_MAX_SIZE + 2 + 1;

char nibble_to_char(uint8_t val) {
    /* val is unsigned so no need to check if < 0 */
    if (9 >= val) {
        return '0' + val;
    } else {
        return 'A' + (val - 10);
    }
}

uint8_t char_to_nibble(char val) {
    uint8_t out = 0x00;

    if (val >= '0' && val <= '9') {
        out = val - '0';
    } else if (val >= 'A' && val <= 'F') {
        out = (val - 'A') + 10;
    } else if (val >= 'a' && val <= 'f') {
        out = (val - 'a') + 10;
    }

    return out;
}

bool isValidHostMsg(char *buf, uint32_t len) {
    /* The length should be a power of 2, have the correct start/end of message 
     * delimiters, and be within the min/max J1708 message sizes */
    return (((len % 2) == 0)
            && (len >= HOST_MSG_MIN_SIZE)
            && (len <= HOST_MSG_MAX_SIZE)
            && (buf[0] == HOST_MSG_START)
            && (buf[len-1] == HOST_MSG_END));
}

void printMsgToHost(J1708Msg src) {
    char out[HOST_MSG_BUF_SIZE];
    int outIdx;

    out[0] = HOST_MSG_START;
    outIdx = 1;

    for (uint32_t i = 0; i < src.len; i++) {
        out[outIdx]     = nibble_to_char((src.buf[i] & 0xF0) >> 4);
        out[outIdx + 1] = nibble_to_char(src.buf[i] & 0x0F);
        outIdx += 2;
    }

    out[outIdx++] = HOST_MSG_END;
    out[outIdx] = '\0';
    SerialUSB.print(out);
}

J1708Msg hostToJ1708Msg(char *buf, uint32_t len) {
    J1708Msg msg;
    if (isValidHostMsg(buf, len)) {
        uint32_t msgIdx = 0;

        /* Skip the SOM and EOM delimiters */
        for (uint32_t i = 1; i < (len - 1); i += 2) {
            msg.buf[msgIdx]  = char_to_nibble(buf[i]) << 4;
            msg.buf[msgIdx] |= char_to_nibble(buf[i + 1]);
            msgIdx++;
        }
        msg.len = msgIdx;
    }

    return msg;
}

/* Normally we'd use the variable name Serial1 for this, but it is already 
 * defined as:
 *
 *      extern HardwareSerial Seriall1;
 *
 * in HardwareSerial.h, even though this project is compiled with the standard 
 * Serial1 object not being created.  So we have to call it something different.
 */
J1708Serial bus(PA10, PA9);

void setup(void) {
    led_setup();

    bus.begin();
}

char incoming[HOST_MSG_BUF_SIZE];
uint32_t received = 0;
uint32_t last = 0;

void loop(void) {
    J1708Msg tmp;
    char readChar;
    uint32_t now = millis();

    /* Slow blink to make it easier to see that the board is on and 
     * functioning. */
    if ((now - last) > 1000) {
        led_toggle();
        last = now;
    }

    /* See if there is any incoming USB data */
    if (SerialUSB.available()) {
        readChar = SerialUSB.read();
        if (readChar == HOST_MSG_START) {
            /* If this is the start of message character reset the received 
             * characters back to 0. */
            received = 0;
            incoming[received++] = readChar;
        } else if ((received > 0) && (received < HOST_MSG_BUF_SIZE)) {
            /* If a message has already started append to the incoming message 
             * buffer. */
            incoming[received++] = readChar;

            if (readChar == HOST_MSG_END) {
#ifdef J1708_TX_DEBUG
                incoming[received] = '\0';
                SerialUSB.print("\nValidating: ");
                SerialUSB.print(incoming);
                SerialUSB.println();
#endif

                /* If this is the end of message character check if this is 
                 * a valid message or not */
                if (isValidHostMsg(incoming, received)) {
                    tmp = hostToJ1708Msg(incoming, received);
                    bus.msgSend(tmp);
                }

                /* Regardless of if this is a valid message or not clear the 
                 * host message buffer. */
                received = 0;
            }
        } else if (received >= HOST_MSG_BUF_SIZE) {
#ifdef J1708_TX_DEBUG
            incoming[HOST_MSG_BUF_SIZE - 1] = '\0';
            SerialUSB.print("\nInvalid msg: ");
            SerialUSB.print(incoming);
            SerialUSB.println();
#endif

            /* clear the host msg buffer */
            received = 0;
        } else {
#ifdef J1708_TX_DEBUG
            SerialUSB.print("\nInvalid SOM: ");
            SerialUSB.print(readChar);
            SerialUSB.print(" (0x");
            SerialUSB.print(readChar, HEX);
            SerialUSB.println(")");
#endif
        }
    } /* if (SerialUSB.available()) */

    /* Now see if there are any messages that have been received */
    if (bus.msgRecv(&tmp)) {
        printMsgToHost(tmp);
    }
}
