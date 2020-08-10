#include <string.h>
#include <stdlib.h>
#include "main.h"
#include "msg.h"
#include "usb.h"

void copy_msg(msg_t *dst, msg_t *src) {
    memcpy((void*) dst, (void*) src, sizeof(msg_t));
}

void copy_to_msg(msg_t *dst, uint8_t *src, uint8_t len) {
    memcpy((void*) dst->buf, (void*) src, len);
    dst->idx = 0;
    dst->len = len;
}

uint8_t copy_from_msg(uint8_t *dst, msg_t *src) {
    memcpy((void*) dst, (void*) src->buf, src->len);
    return src->len;
}

static char nibble_to_char(uint8_t val) {
    /* val is unsigned so no need to check if < 0 */
    if (9 >= val) {
        return '0' + val;
    } else {
        return 'A' + (val - 10);
    }
}

void j1708_to_host(msg_t *msg) {
    msg_t out = MSG_INIT;

    out.buf[out.idx++] = HOST_MSG_START;

    for (uint8_t i = 0; i < msg->len; i++) {
        out.buf[out.idx++] = nibble_to_char((msg->buf[i] & 0xF0) >> 4);
        out.buf[out.idx++] = nibble_to_char(msg->buf[i] & 0x0F);
    }

    out.buf[out.idx++] = HOST_MSG_END;
    out.len = out.idx;

    /* Now send this to the host */
    usb_write(out.buf, out.len);
}

void host_to_j1708(msg_t *msg) {
    msg_t out = MSG_INIT;
    char byte_str[3] = { 0 };
    uint32_t val;

    /* The USB receive procedure already removes the message delimiters, so just 
     * convert the bytes. */
    for (uint8_t i = 0; i < msg->len; i += 2) {
        byte_str[0] = msg->buf[i];
        byte_str[1] = msg->buf[i + 1];

        val = (uint32_t) strtol(byte_str, (char **)NULL, 16);

        out.buf[out.idx++] = val;
    }
    out.len = out.idx;

    /* Now send this out the J1708 UART */
    j1708_write(out.buf, out.len);
}
