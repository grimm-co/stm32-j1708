#include "J1708Serial.h"
#include "led.h"

/* Start/end message delimiters */
const char HOST_MSG_START = '$';
const char HOST_MSG_END   = '*';

const uint32_t HOST_MSG_MIN_SIZE = J1708_MSG_MIN_SIZE * 2;
const uint32_t HOST_MSG_MAX_SIZE = J1708_MSG_MAX_SIZE * 2;

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

bool isValidHostMsg(uint8_t *buf, uint32_t len) {
    /* The length should be a power of 2, have the correct start/end of message 
     * delimiters, and be within the min/max J1708 message sizes */
    return (len > 0) && ((len % 2) == 0) &&
        (len >= HOST_MSG_MIN_SIZE) && (len <= HOST_MSG_MAX_SIZE) &&
        (buf[0] == HOST_MSG_START) && (buf[len-1] == HOST_MSG_END);
}

void printMsgToHost(J1708Msg* src) {
    char out[HOST_MSG_BUF_SIZE];
    int outIdx;

    out[0] = HOST_MSG_START;
    outIdx = 1;

    for (uint32_t i = 0; i < src->len; i++) {
        out[outIdx]     = nibble_to_char((src->buf[i] & 0xF0) >> 4);
        out[outIdx + 1] = nibble_to_char(src->buf[i] & 0x0F);
        outIdx += 2;
    }

    out[outIdx++] = HOST_MSG_END;
    out[outIdx] = '\0';
    SerialUSB.print(out);

    /* Now that the message has been sent deallocate it */
    delete src;
}

J1708Msg* newFromHostMsg(uint8_t *buf, uint32_t len) {
    J1708Msg* msg = NULL;

    if (isValidHostMsg(buf, len)) {
        uint32_t msgIdx = 0;

        msg = new J1708Msg();

        /* Skip the SOM and EOM delimiters */
        for (uint32_t i = 1; i < (len - 1); i += 2) {
            msg->buf[msgIdx]  = char_to_nibble(buf[i]) << 4;
            msg->buf[msgIdx] |= char_to_nibble(buf[i + 1]);
            msgIdx++;
        }
        msg->len = msgIdx;
    }

    return msg;
}

HardwareSerial Serial1(PA10, PA9);
J1708Serial J1708Device(&Serial1, PA10, PA9);

void setup() {
    led_setup();

    J1708Device.begin();
}

uint8_t incoming[HOST_MSG_BUF_SIZE];
uint32_t received = 0;

void loop() {
    J1708Msg *tmp;
    uint8_t readChar;

    /* See if there is any incoming USB data */
    readChar = SerialUSB.read();
    if (readChar != -1) {
        /* If no command chars have been received yet, don't save incoming 
         * characters unless it is the SOM character */
        if (((received == 0) && (readChar == HOST_MSG_START)) ||
            (received > 0)) {
            incoming[received++] = readChar;

            /* See if this is a complete valid message yet or not */
            tmp = newFromHostMsg(incoming, received);
            if (tmp != NULL) {
                J1708Device.write(tmp);

                /* Reset the incoming msg buffer */
                received = 0;
            }
        }
    }

    /* Now see if there are any messages that have been received */
    tmp = J1708Device.read();
    if (tmp != NULL) {
        printMsgToHost(tmp);
    }
}
