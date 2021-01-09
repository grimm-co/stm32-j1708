#ifndef __J1708SERIAL_H__
#define __J1708SERIAL_H__

#include <HardwareSerial.h>
#include "queue.h"
#include "OneShotHardwareTimer.h"
#include <PeripheralPins.h>

extern "C" {

/* This function is in libraries/SrcWrapper/src/stm32/uart.c but doesn't have 
 * a prototype in the header files. */
serial_t *get_serial_obj(UART_HandleTypeDef *huart);

}

/* The "End Of Message" and "Tx Collision" timers must be initialized in the 
 * class definition, so these macros can be used to configure which timers 
 * should be used */
#ifndef J1708_EOM_TIMER
#define J1708_EOM_TIMER TIM2
#endif

#ifndef J1708_COL_TIMER
#define J1708_COL_TIMER TIM3
#endif

/* Standard serial settings from the J1708 standard */
const uint32_t J1708_BAUD  = 9600;
const uint8_t J1708_CONFIG = SERIAL_8N1;

/* According to the SAE J1708 standard the maximum message length is 21 bytes */
const uint32_t J1708_MSG_MAX_SIZE = 21;
const uint32_t J1708_MSG_MIN_SIZE = 2;

typedef struct {
    uint8_t buf[J1708_MSG_MAX_SIZE];
    uint32_t len;
} J1708Msg;

/* Assuming things work properly the message queues shouldn't need to be be very 
 * deep */
const uint32_t J1708_MSG_QUEUE_DEPTH = 64;

class J1708Serial {
public:
    /* Too bad that the Tx/Rx pin names must be supplied explicitly for now, 
     * can't figure out how to get the serial_t object out of the HardwareSerial 
     * device directly.  And I can't subclass HardwareSerial because somehow the 
     * object is already created in the system libraries and I can't stop it 
     * from being created. */
    J1708Serial(HardwareSerial *dev, int _tx, int _rx) {
        J1708Serial::_txAvail = true;

        // Update the static hardware pointer
        J1708Serial::_hwDev = dev;

        /* Get the tx and rx pin objects */
        USART_TypeDef *uart_tx = (USART_TypeDef*) pinmap_peripheral((PinName)_tx, PinMap_UART_TX);
        USART_TypeDef *uart_rx = (USART_TypeDef*) pinmap_peripheral((PinName)_rx, PinMap_UART_RX);

        /* Now get the UART handle object */
        UART_HandleTypeDef *uart = (UART_HandleTypeDef*) pinmap_merge_peripheral(uart_tx, uart_rx);

        /* Finally we can locate the serial device handle */
        J1708Serial::_serial = get_serial_obj(uart);
    }

    /* Timer callbacks */
    static void _eomCallback(void);
    static void _colCallback(void);

    bool available(void);
    J1708Msg read(void);
    void write(J1708Msg msg);

    /* Modified function to add J1708 timer stuff */
    static void _rx_complete_irq(serial_t *obj);

    void begin(void) {
        /* Configure the J1708 message timers */
        configure();

        /* Start the supplied UART */
        J1708Serial::_hwDev->begin(J1708_BAUD, J1708_CONFIG);

        /* Install our own Rx ISR */
        uart_attach_rx_callback(J1708Serial::_serial, _rx_complete_irq);

        /* Flush any data that has already been received */
        while (J1708Serial::_hwDev->read() != -1);
    }

private:
    void configure(void);

    /* Internal send/receive utilities */
    bool _sendMsg(J1708Msg msg);
    J1708Msg _getMsg(void);
    bool _isTxAllowed(void);
    void _handleTxCollision(void);

    static bool _txAvail;

    static HardwareSerial *_hwDev;
    static serial_t *_serial;

    static Queue<J1708Msg> _rxMsgs;
    static Queue<J1708Msg> _txMsgs;

    static OneShotHardwareTimer _EOMTimer;
    static OneShotHardwareTimer _COLTimer;
};

#endif /* __J1708SERIAL_H__ */
