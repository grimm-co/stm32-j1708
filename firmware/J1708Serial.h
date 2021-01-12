#ifndef __J1708SERIAL_H__
#define __J1708SERIAL_H__

#include <Arduino.h>
#include <HardwareSerial.h>
#include "queue.h"
#include "OneShotHardwareTimer.h"
#include "led.h"

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
const uint32_t J1708_BAUD     = 9600;
const uint32_t J1708_NUMBITS  = UART_WORDLENGTH_8B;
const uint32_t J1708_PARITY   = UART_PARITY_NONE;
const uint32_t J1708_STOPBITS = UART_STOPBITS_1;

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

class J1708Serial : public HardwareSerial {
public:
    J1708Serial(int _tx, int _rx) :
        HardwareSerial(_tx, _rx)
    {
        /* Save the _serial object to our static pointer variable to let the 
         * callbacks access the serial object. */
        _serialPtr = &_serial;
    }

    /* Timer callbacks */
    static void _eomCallback(void);
    static void _colCallback(void);

    /* parent class virtual functions we must define */
    virtual int available(void);
    virtual int peek(void);
    virtual int read(void);
    virtual void flush(void);
    virtual size_t write(uint8_t);

    /* New J1708-specific message send/recv functions */
    bool msgAvailable(void);
    bool msgRecv(J1708Msg *msg);
    void msgSend(J1708Msg msg);

    void begin(void);

private:
    /* Modified function to add J1708 timer stuff */
    static void _rx_complete_irq(serial_t *obj);

    void configure(void);

    /* Internal send/receive utilities */
    bool _isTxAllowed(void);
    void _handleTxCollision(void);

    static serial_t *_serialPtr;
    static bool _txAvail;

    static Queue<J1708Msg> _rxMsgs;
    static Queue<J1708Msg> _txMsgs;

    static OneShotHardwareTimer _EOMTimer;
    static OneShotHardwareTimer _COLTimer;
};

#endif /* __J1708SERIAL_H__ */
