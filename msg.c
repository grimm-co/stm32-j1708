#include <string.h>
#include <stdlib.h>
#include "msg.h"

void msg_init(msg_t *msg) {
    memset(msg, 0, sizeof(msg_t));
}

void msg_queue_init(msg_queue_t *queue) {
    memset(queue, 0, sizeof(msg_queue_t));

    /* Not strictly necessary but I like to be explicit about such things as 
     * lock initialization values. */
    queue->lock = MUTEX_UNLOCKED;
}

bool msg_avail(msg_queue_t *queue) {
    bool answer = false;

    LOCK(queue);
    if (queue->oldest != queue->newest) {
        answer = true;
    }
    UNLOCK(queue);

    return answer;
}

bool msg_pop(msg_queue_t *queue, msg_t *dst) {
    bool valid = false;

    LOCK(queue);
    if (queue->oldest != queue->newest) {
        valid = true;
        /* Copy the message into the supped buffer */
        memcpy((void*)dst, (void*)&queue->msgs[queue->oldest], sizeof(msg_t));

        /* Move the oldest pointer to the next index */
        queue->oldest++;
        if (queue->oldest >= MSG_QUEUE_SIZE) {
            queue->oldest = 0;
        }
    }
    UNLOCK(queue);

    return valid;
}

void msg_push(msg_queue_t *queue, msg_t *msg) {
    LOCK(queue);

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
    memcpy((void*) &queue->msgs[queue->newest], (void*)msg, sizeof(msg_t));

    UNLOCK(queue);
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

char nibble_to_char(uint8_t val) {
    /* val is unsigned so no need to check if < 0 */
    if (9 >= val) {
        return '0' + val;
    } else {
        return 'A' + (val - 10);
    }
}

void byte_to_hex(char *buf, uint8_t val) {
    buf[0] = nibble_to_char((val & 0xF0) >> 4);
    buf[1] = nibble_to_char(val & 0x0F);
}

uint8_t char_to_nibble(char val) {
    uint8_t out = 0x00;

    if (val >= '0' && val <= '9') {
        out = val - '0';
    } else if (val >= 'A' && val <= 'F') {
        out = val - 'A';
    } else if (val >= 'a' && val <= 'f') {
        out = val - 'a';
    }

    return out;
}

uint8_t hex_to_byte(char *buf) {
    uint8_t out;

    out = char_to_nibble(buf[0]) << 4;
    out |= char_to_nibble(buf[1]) << 4;

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

void to_host_msg(msg_t *dst, uint8_t *src, uint32_t len) {
    uint32_t dst_idx;
    dst->buf[0] = HOST_MSG_START;
    dst_idx = 1;

    for (uint32_t i = 0; i < len; i++) {
        byte_to_hex((char*) &dst->buf[dst_idx], src[i]);
        dst_idx += 2;
    }

    dst->buf[dst_idx] = HOST_MSG_END;
    dst->len = dst_idx + 1;
}

void from_host_msg(msg_t *dst, uint8_t *src, uint32_t len) {
    uint32_t dst_idx = 0;

    /* The USB receive procedure already removes the message delimiters, so just 
     * convert the bytes. */
    for (uint32_t i = 0; i < len; i += 2) {
        dst->buf[dst_idx++] = hex_to_byte((char*) &src[i]);
    }
    dst->len = dst_idx;
}
