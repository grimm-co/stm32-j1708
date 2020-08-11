#ifndef __MSG_H__
#define __MSG_H__

#include "j1708.h"

/* The J1708 message will be transformed into printable HEX chars for sending to 
 * the USB host.  We need 2x the number of bytes as the max J1708 message size 
 * +2 for the start and end message characters */
#define HOST_MAX_MSG_SIZE ((J1708_MAX_MSG_SIZE * 2) + 2)

/* Start/end message delimiters */
#define HOST_MSG_START '$'
#define HOST_MSG_END   '*'

/* Message type that is used for both the J1708 and USB ISRs to store incoming 
 * messages */
typedef struct {
    volatile uint8_t idx;
    volatile uint8_t len;
    volatile uint8_t buf[HOST_MAX_MSG_SIZE];
} msg_t;

#define MSG_INIT \
{ \
    .idx = 0, \
    .len = 0, \
    .buf = { \
        [0 ... HOST_MAX_MSG_SIZE-1] = 0x00 \
    } \
}

void copy_msg(msg_t *dst, msg_t *src);
void copy_to_msg(msg_t *dst, uint8_t *src, uint8_t len);
uint8_t copy_from_msg(uint8_t *dst, msg_t *src);

void j1708_to_host(msg_t *msg);
void host_to_j1708(msg_t *msg);

#endif // __MSG_H__
