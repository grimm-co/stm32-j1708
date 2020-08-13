#ifndef __J1708_H__
#define __J1708_H__

#include <stdint.h>
#include <stdbool.h>
#include "msg.h"

#define J1708_BAUD 9600

/* According to the SAE J1708 standard the timeout for end of a message is 10 
 * "bit times" the baud rate is 9600 the timeout Hz is 9600 / 10 =  960.
 * According to my testing, we need a slightly longer timeout, perhaps the 
 * timing on the STM32 device is too precise?  Or perhaps I a measuring from the 
 * wrong point. */
#define J1708_MSG_TIMEOUT (10 + 1)

/* The priority idle time (when a tx collision occurs) */
#define J1708_COLLISION_WAIT(msg_priority) (J1708_MSG_TIMEOUT + ((msg_priority) * 2))

/* According to the SAE J1708 standard the maximum message length is 21 bytes */
#define J1708_MAX_MSG_SIZE 21

void j1708_setup(void);
bool j1708_msg_avail(void);
bool j1708_read_msg(msg_t *msg);
void j1708_write_msg(msg_t *msg);
uint32_t j1708_msg_priority(msg_t *msg);

#endif // __J1708_H__
