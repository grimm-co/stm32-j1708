#ifndef __MAIN_H__
#define  __MAIN_H__

/* Define which interrupts have priority:
 * 0: systick may not be enabled but if it was it should have highest priority
 * 1: USB is next highest priority to ensure that a busy J1708 bus does not
 *    prevent the USB bus from working.
 * 2: USART (J1708) is the next highest priority
 * 3: Timers are the last priority we define, they should be lower priority than
 *    the USART (J1708) interrupts because USART activity controls if timers are
 *    running or not. */
#define SYSTICK_IRQ_PRI 0
#define USB_IRQ_PRI     1
#define J1708_IRQ_PRI   2
#define TIMER_IRQ_PRI   3

#define UNUSED __attribute__((unused))
#define ISR __attribute__((unused))

#endif // __MAIN_H__
