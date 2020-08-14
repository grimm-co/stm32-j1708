/*
 * This file is part of the libopencm3 project.
 *
 * Copyright (C) 2010 Gareth McMullin <gareth@blacksphere.co.nz>
 *
 * This library is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/desig.h>
#include <libopencm3/usb/cdc.h>
#include <libopencm3/cm3/nvic.h>
#include <libopencm3/cm3/sync.h>
#include "main.h"
#include "usb.h"

#define USB_EP_IN  0x01
#define USB_EP_OUT 0x82
#define USB_EP_INT 0x83

static const struct usb_device_descriptor dev = {
    .bLength = USB_DT_DEVICE_SIZE,
    .bDescriptorType = USB_DT_DEVICE,
    .bcdUSB = 0x0200,
    .bDeviceClass = USB_CLASS_CDC,
    .bDeviceSubClass = 0,
    .bDeviceProtocol = 0,
    .bMaxPacketSize0 = USB_PACKET_SIZE,
    .idVendor = 0x0483,
    .idProduct = 0x5740,
    .bcdDevice = 0x0200,
    .iManufacturer = 1,
    .iProduct = 2,
    .iSerialNumber = 3,
    .bNumConfigurations = 1,
};

/*
 * This notification endpoint isn't implemented. According to CDC spec its
 * optional, but its absence causes a NULL pointer dereference in Linux
 * cdc_acm driver.
 */
static const struct usb_endpoint_descriptor comm_endp[] = {{
    .bLength = USB_DT_ENDPOINT_SIZE,
    .bDescriptorType = USB_DT_ENDPOINT,
    .bEndpointAddress = USB_EP_INT,
    .bmAttributes = USB_ENDPOINT_ATTR_INTERRUPT,
    .wMaxPacketSize = 16,
    .bInterval = 255,
}};

static const struct usb_endpoint_descriptor data_endp[] = {{
    .bLength = USB_DT_ENDPOINT_SIZE,
    .bDescriptorType = USB_DT_ENDPOINT,
    .bEndpointAddress = USB_EP_IN,
    .bmAttributes = USB_ENDPOINT_ATTR_BULK,
    .wMaxPacketSize = USB_PACKET_SIZE,
    .bInterval = 1,
}, {
    .bLength = USB_DT_ENDPOINT_SIZE,
    .bDescriptorType = USB_DT_ENDPOINT,
    .bEndpointAddress = USB_EP_OUT,
    .bmAttributes = USB_ENDPOINT_ATTR_BULK,
    .wMaxPacketSize = USB_PACKET_SIZE,
    .bInterval = 1,
}};

static const struct {
    struct usb_cdc_header_descriptor header;
    struct usb_cdc_call_management_descriptor call_mgmt;
    struct usb_cdc_acm_descriptor acm;
    struct usb_cdc_union_descriptor cdc_union;
} __attribute__((packed)) cdcacm_functional_descriptors = {
    .header = {
        .bFunctionLength = sizeof(struct usb_cdc_header_descriptor),
        .bDescriptorType = CS_INTERFACE,
        .bDescriptorSubtype = USB_CDC_TYPE_HEADER,
        .bcdCDC = 0x0110,
    },
    .call_mgmt = {
        .bFunctionLength =
            sizeof(struct usb_cdc_call_management_descriptor),
        .bDescriptorType = CS_INTERFACE,
        .bDescriptorSubtype = USB_CDC_TYPE_CALL_MANAGEMENT,
        .bmCapabilities = 0,
        .bDataInterface = 1,
    },
    .acm = {
        .bFunctionLength = sizeof(struct usb_cdc_acm_descriptor),
        .bDescriptorType = CS_INTERFACE,
        .bDescriptorSubtype = USB_CDC_TYPE_ACM,
        .bmCapabilities = 0,
    },
    .cdc_union = {
        .bFunctionLength = sizeof(struct usb_cdc_union_descriptor),
        .bDescriptorType = CS_INTERFACE,
        .bDescriptorSubtype = USB_CDC_TYPE_UNION,
        .bControlInterface = 0,
        .bSubordinateInterface0 = 1,
     },
};

static const struct usb_interface_descriptor comm_iface[] = {{
    .bLength = USB_DT_INTERFACE_SIZE,
    .bDescriptorType = USB_DT_INTERFACE,
    .bInterfaceNumber = 0,
    .bAlternateSetting = 0,
    .bNumEndpoints = 1,
    .bInterfaceClass = USB_CLASS_CDC,
    .bInterfaceSubClass = USB_CDC_SUBCLASS_ACM,
    .bInterfaceProtocol = USB_CDC_PROTOCOL_AT,
    .iInterface = 0,

    .endpoint = comm_endp,

    .extra = &cdcacm_functional_descriptors,
    .extralen = sizeof(cdcacm_functional_descriptors),
}};

static const struct usb_interface_descriptor data_iface[] = {{
    .bLength = USB_DT_INTERFACE_SIZE,
    .bDescriptorType = USB_DT_INTERFACE,
    .bInterfaceNumber = 1,
    .bAlternateSetting = 0,
    .bNumEndpoints = 2,
    .bInterfaceClass = USB_CLASS_DATA,
    .bInterfaceSubClass = 0,
    .bInterfaceProtocol = 0,
    .iInterface = 0,

    .endpoint = data_endp,
}};

static const struct usb_interface ifaces[] = {{
    .num_altsetting = 1,
    .altsetting = comm_iface,
}, {
    .num_altsetting = 1,
    .altsetting = data_iface,
}};

static const struct usb_config_descriptor config = {
    .bLength = USB_DT_CONFIGURATION_SIZE,
    .bDescriptorType = USB_DT_CONFIGURATION,
    .wTotalLength = 0,
    .bNumInterfaces = 2,
    .bConfigurationValue = 1,
    .iConfiguration = 0,
    .bmAttributes = 0x80,
    .bMaxPower = 0x32,

    .interface = ifaces,
};

/* The UID for the STM32 device is 3 32bit values, each byte is 2 chars, so the 
 * total length for the UID string is (3 * 4 * 2) + 1 (for null char) */
#define UID_LEN ((3 * 4 * 2) + 1)
static char uid_buf[UID_LEN];

static const char *usb_strings[] = {
    "GRIMM j1708cat (WIP)",
    "SAE J1708 Reader",
    uid_buf,
};

/* Buffer to be used for control requests. */
uint8_t usbd_control_buffer[128];

static enum usbd_request_return_codes cdcacm_control_request(
    UNUSED usbd_device *usbd_dev,
    struct usb_setup_data *req,
    UNUSED uint8_t **buf,
    uint16_t *len,
    UNUSED void (**complete)(usbd_device *usbd_dev, struct usb_setup_data *req)) {
    switch (req->bRequest) {
    case USB_CDC_REQ_SET_CONTROL_LINE_STATE: {
        /*
         * This Linux cdc_acm driver requires this to be implemented
         * even though it's optional in the CDC spec, and we don't
         * advertise it in the ACM functional descriptor.
         */
        char local_buf[10];
        struct usb_cdc_notification *notif = (void *)local_buf;

        /* We echo signals back to host as notification. */
        notif->bmRequestType = 0xA1;
        notif->bNotification = USB_CDC_NOTIFY_SERIAL_STATE;
        notif->wValue = 0;
        notif->wIndex = 0;
        notif->wLength = 2;
        local_buf[8] = req->wValue & 3;
        local_buf[9] = 0;
        return USBD_REQ_HANDLED;
    }
    case USB_CDC_REQ_SET_LINE_CODING:
        if (*len < sizeof(struct usb_cdc_line_coding))
            return USBD_REQ_NOTSUPP;
        return USBD_REQ_HANDLED;
    }
    return USBD_REQ_NOTSUPP;
}

volatile bool usb_ready = false;

static void cdcacm_reset(void) {
  usb_ready = false;
}

static msg_queue_t usb_queue;

static void cdcacm_data_rx_cb(usbd_device *usbd_dev, UNUSED uint8_t ep) {
    uint8_t buf[USB_PACKET_SIZE];
    uint32_t len;
    msg_t msg;

    /* Get the message from the USB host */
    len = usbd_ep_read_packet(usbd_dev, USB_EP_IN, buf, USB_PACKET_SIZE);

    if (is_valid_host_msg(buf, len)) {
        /* If the message is valid convert it from the host msg format and then 
         * save it */
        from_host_msg(&msg, buf, len);
        msg_push(&usb_queue, &msg);
    }
}

static void cdcacm_set_config(usbd_device *usbd_dev, uint16_t wValue) {
    usbd_ep_setup(usbd_dev, USB_EP_IN, USB_ENDPOINT_ATTR_BULK, USB_PACKET_SIZE, cdcacm_data_rx_cb);
    usbd_ep_setup(usbd_dev, USB_EP_OUT, USB_ENDPOINT_ATTR_BULK, USB_PACKET_SIZE, NULL);
    usbd_ep_setup(usbd_dev, USB_EP_INT, USB_ENDPOINT_ATTR_INTERRUPT, 16, NULL);

    usbd_register_control_callback(
                usbd_dev,
                USB_REQ_TYPE_CLASS | USB_REQ_TYPE_INTERFACE,
                USB_REQ_TYPE_TYPE | USB_REQ_TYPE_RECIPIENT,
                cdcacm_control_request);

    if (wValue > 0) {
        usb_ready = true;
    }
}

static usbd_device *usbd_dev;

#ifdef USB_POLL_INTERRUPTS
void usb_wakeup_isr(void) {
  usbd_poll(usbd_dev);
}

void usb_hp_can_tx_isr(void) {
  usbd_poll(usbd_dev);
}

void usb_lp_can_rx0_isr(void) {
  usbd_poll(usbd_dev);
}
#endif

void usb_setup(void) {
    msg_queue_init(&usb_queue);

    /* Needed for USB */
    rcc_periph_clock_enable(RCC_GPIOA);

    memset((void*) uid_buf, 0, UID_LEN);
    desig_get_unique_id_as_string(uid_buf, UID_LEN);

    usbd_dev = usbd_init(&st_usbfs_v1_usb_driver, &dev, &config,
                         usb_strings, 3,
                         usbd_control_buffer, sizeof(usbd_control_buffer));

    usbd_register_set_config_callback(usbd_dev, cdcacm_set_config);
    usbd_register_reset_callback(usbd_dev, cdcacm_reset);

#ifdef USB_POLL_INTERRUPTS
    /* NOTE: Must be called after USB setup since this enables calling usbd_poll(). */
    nvic_enable_irq(NVIC_USB_HP_CAN_TX_IRQ);
    nvic_enable_irq(NVIC_USB_LP_CAN_RX0_IRQ);
    nvic_enable_irq(NVIC_USB_WAKEUP_IRQ);

    nvic_set_priority(NVIC_USB_HP_CAN_TX_IRQ, USB_IRQ_PRI);
    nvic_set_priority(NVIC_USB_LP_CAN_RX0_IRQ, USB_IRQ_PRI);
    nvic_set_priority(NVIC_USB_WAKEUP_IRQ, USB_IRQ_PRI);
#endif
}

void usb_poll(void) {
  usbd_poll(usbd_dev);
}

bool usb_connected(void) {
    return usb_ready;
}

bool usb_msg_avail(void) {
    return msg_avail(&usb_queue);
}

bool usb_read_msg(msg_t* msg) {
    return msg_pop(&usb_queue, msg);
}

uint32_t usb_read(uint8_t *buf) {
    uint32_t len = 0;
    msg_t *msg;

    LOCK(&usb_queue);
    msg = msg_pop_nolock(&usb_queue);
    if (msg != NULL) {
        memcpy((void*)buf, (void*)msg->buf, msg->len);
        len = msg->len;
    }
    UNLOCK(&usb_queue);

    return len;
}

void usb_write_msg(msg_t* msg) {
    /* Just ignore the return value, the write probably worked.  And we've got 
     * no good way if a write was not successful. */
    (void)usb_write(msg->buf, msg->len);
}

uint32_t usb_write(uint8_t *buf, uint32_t len) {
    uint16_t chunk_len, ret;
    uint32_t written = 0;

    do {
        if (len > USB_PACKET_SIZE) {
            chunk_len = USB_PACKET_SIZE;
        } else {
            chunk_len = len;
        }
        ret = usbd_ep_write_packet(usbd_dev, USB_EP_OUT, (void*) &buf[written], chunk_len);

        if (ret == 0) {
            return 0;
        } else {
            written += ret;
        }
    } while (len > written);

    return written;
}

/* Define _write so stdio.h functions work */
int _write(int file, char *ptr, int len);
int _write(int file, char *ptr, int len) {
    /* 1 == STDOUT */
    if (file == 1) {
        return (int) usb_write((uint8_t*) ptr, len);
    }

    errno = EIO;
    return -1;
}
