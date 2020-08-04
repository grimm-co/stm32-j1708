#ifndef __J1708_H__
#define __J1708_H__

/* According to the SAE J1708 standard the timeout for end of a message is 10 
 * "bit times" the baud rate is 9600 the timeout Hz is 9600 / 10 =  960. */
#define J1708_BAUD 9600
#define J1708_MSG_TIMEOUT 10

/* The priority if this "node", set to lowest (8) */
#define J1708_NODE_PRIORITY 8

/* The priority idle time (when a tx collision occurs) */
#define J1708_COLLISION_WAIT (J1708_MSG_TIMEOUT + (J1708_NODE_PRIORITY * 2))

/* According to the SAE J1708 standard the maximum message length is 21 bytes */
#define J1708_MAX_MSG_SIZE 21

void j1708_setup(void);
bool j1708_msg_avail(void);
uint8_t j1708_read(uint8_t *buf);
void j1708_write(uint8_t *buf, uint8_t len);

#endif // __J1708_H__
