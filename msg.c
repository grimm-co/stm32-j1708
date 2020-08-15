#include <string.h>
#include <stdlib.h>
#include "msg.h"

void msg_init(msg_t *msg) {
    memset(msg, 0, sizeof(msg_t));
}

void msg_queue_init(msg_queue_t *queue) {
    memset(queue, 0, sizeof(msg_queue_t));
}

bool msg_avail(msg_queue_t *queue) {
    bool answer = false;

    CM_ATOMIC_CONTEXT();
    if (queue->oldest != queue->newest) {
        answer = true;
    }

    return answer;
}

bool msg_pop(msg_queue_t *queue, msg_t *dst) {
    bool valid = false;

    CM_ATOMIC_CONTEXT();
    if (queue->oldest != queue->newest) {
        valid = true;
        /* Copy the message into the supped buffer */
        memcpy(dst, &queue->msgs[queue->oldest], sizeof(msg_t));

        /* Move the oldest pointer to the next index */
        queue->oldest++;
        if (queue->oldest >= MSG_QUEUE_SIZE) {
            queue->oldest = 0;
        }
    }

    return valid;
}

bool msg_push_buf(msg_queue_t *queue, uint8_t *buf, uint32_t len) {
    CM_ATOMIC_CONTEXT();
    return msg_push_buf(queue, buf, len);
}

bool msg_push_buf_nolock(msg_queue_t *queue, uint8_t *buf, uint32_t len) {
    if (len > 0) {
        /* Increment the newest pointer to the new index we should place this 
         * message at. */
        queue->newest++;
        if (queue->newest >= MSG_QUEUE_SIZE) {
            queue->newest = 0;
        }

        /* If newest now is the same as oldest, increment oldest because we are 
         * overwriting the oldest message. */
        if (queue->oldest == queue->newest) {
            queue->oldest++;
        }

        /* Save the message in the newest index. */
        memcpy(&queue->msgs[queue->newest].buf, buf, len);
        queue->msgs[queue->newest].len = len;

        return true;
    } else {
        return false;
    }
}

bool msg_push_nolock(msg_queue_t *queue, msg_t *msg) {
    return msg_push_buf_nolock(queue, msg->buf, msg->len);
}

bool msg_push(msg_queue_t *queue, msg_t *msg) {
    CM_ATOMIC_CONTEXT();
    return msg_push_nolock(queue, msg);
}

msg_t* msg_pop_nolock(msg_queue_t *queue) {
    msg_t *msg = NULL;

    if (queue->oldest != queue->newest) {
        /* Just get a pointer to the message */
        msg = &queue->msgs[queue->oldest];

        /* Move the oldest pointer to the next index */
        queue->oldest++;
        if (queue->oldest >= MSG_QUEUE_SIZE) {
            queue->oldest = 0;
        }
    }

    return msg;
}

static char nibble_to_char(uint8_t val) {
    /* val is unsigned so no need to check if < 0 */
    if (9 >= val) {
        return '0' + val;
    } else {
        return 'A' + (val - 10);
    }
}

static uint8_t char_to_nibble(char val) {
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

bool is_valid_host_msg(uint8_t *buf, uint32_t len) {
    /* The length should be a power of 2 and have the correct start/end of 
     * message delimiters. */
    if ((len > 0) && ((len % 2) == 0) &&
        (buf[0] == HOST_MSG_START) && (buf[len-1] == HOST_MSG_END)) {
        return true;
    } else {
        return false;
    }
}

void to_host_msg(msg_t *dst, msg_t *src) {
    uint32_t dst_idx;

    dst->buf[0] = HOST_MSG_START;
    dst_idx = 1;

    for (uint32_t i = 0; i < src->len; i++) {
        dst->buf[dst_idx]     = nibble_to_char((src->buf[i] & 0xF0) >> 4);
        dst->buf[dst_idx + 1] = nibble_to_char(src->buf[i] & 0x0F);
        dst_idx += 2;
    }

    dst->buf[dst_idx] = HOST_MSG_END;
    dst->len = dst_idx + 1;
}

bool from_host_msg(msg_t *dst, msg_t *src) {
    uint32_t dst_idx = 0;

    if (is_valid_host_msg(src->buf, src->len)) {
        /* Skip the SOM and EOM delimiters */
        for (uint32_t i = 1; i < (src->len - 1); i += 2) {
            dst->buf[dst_idx]  = char_to_nibble(src->buf[i]) << 4;
            dst->buf[dst_idx] |= char_to_nibble(src->buf[i + 1]);
            dst_idx++;
        }
        dst->len = dst_idx;

        return true;
    } else {
        return false;
    }
}
