#ifndef __USB_H__
#define __USB_H__

void usb_setup(void);

bool usb_connected(void);
bool usb_msg_avail(void);
uint8_t usb_read(uint8_t *buf);
void usb_write(uint8_t *buf, uint8_t len);

#endif // __USB_H__
