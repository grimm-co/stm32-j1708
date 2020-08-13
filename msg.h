#ifndef __MSG_H__
#define __MSG_H__

#include <stdint.h>
#include <stdbool.h>
#include <libopencm3/cm3/sync.h>

/* The J1708 message will be transformed into printable HEX chars for sending to 
 * the USB host.  We need 2x the number of bytes as the max J1708 message size 
 * +2 for the start and end message characters.
 *  HOST_MAX_MSG_SIZE ((J1708_MAX_MSG_SIZE * 2) + 2)
 *
 * But for the ease of buffer management use the maximum USB msg size (64) */
#define MSG_BUF_SIZE 64

#define MSG_QUEUE_SIZE 10

/* Start/end message delimiters */
#define HOST_MSG_START '$'
#define HOST_MSG_END   '*'

/* Message type that is used for both the J1708 and USB ISRs to store incoming 
 * messages */
typedef struct {
    uint8_t buf[MSG_BUF_SIZE];
    uint32_t len;
} msg_t;

typedef struct {
    mutex_t lock;
    msg_t msgs[MSG_QUEUE_SIZE];
    uint32_t oldest;
    uint32_t newest;
} msg_queue_t;

void msg_init(msg_t *msg);
void msg_queue_init(msg_queue_t *queue);
bool msg_avail(msg_queue_t *queue);

bool msg_pop(msg_queue_t *queue, msg_t *dst);
void msg_push(msg_queue_t *queue, msg_t *src);

#define LOCK(queue)     mutex_lock(&(queue)->lock)
#define UNLOCK(queue)   mutex_unlock(&(queue)->lock)
msg_t* msg_pop_nolock(msg_queue_t *queue);

char nibble_to_char(uint8_t val);
void byte_to_hex(char *buf, uint8_t val);
uint8_t char_to_nibble(char val);
uint8_t hex_to_byte(char *buf);

bool is_valid_host_msg(uint8_t *buf, uint32_t len);
void to_host_msg(msg_t *dst, uint8_t *src, uint32_t len);
void from_host_msg(msg_t *dst, uint8_t *src, uint32_t len);

#endif // __MSG_H__
