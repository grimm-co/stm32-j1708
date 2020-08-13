#ifndef __USB_H__
#define __USB_H__

#include "msg.h"

/* Largest USB msg that can be sent in one packet */
#define USB_PACKET_SIZE 64

void usb_setup(void);

bool usb_connected(void);
bool usb_msg_avail(void);
bool usb_read_msg(msg_t* msg);
uint32_t usb_read(uint8_t *buf);
void usb_write_msg(msg_t* msg);
uint32_t usb_write(uint8_t *buf, uint32_t len);

#endif // __USB_H__
