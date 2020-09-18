#ifndef __USB_H__
#define __USB_H__

#include <stdint.h>
#include <stdbool.h>
#include "msg.h"

/* Largest USB msg that can be sent in one packet */
#define USB_PACKET_SIZE 64
#define USB_INT_PACKET_SIZE 16

void usb_setup(void);
void usb_poll(void);

bool usb_connected(void);
#if 0
bool usb_msg_avail(void);
#endif
bool usb_read_msg(msg_t* msg);
#if 0
uint32_t usb_read(uint8_t *buf);
#endif
void usb_write_msg(msg_t* msg);
#if 0
uint32_t usb_write(uint8_t *buf, uint32_t len);
#endif

#endif // __USB_H__
