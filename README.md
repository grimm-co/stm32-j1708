# Usage
You can capture J1708 messages by connecting the STM32 board to the J1708 bus, 
connecting USB to your computer and running:
```
$ j1708dump
```

If you don't want the J1708 messages decoded you can supply the `-N` option:
```
$ j1708dump -N
```

# Programming
If you have an STLinkV2 programmer connected to your target board you can 
program it with the following command:
```
$ make flash
```

# About
USB CDC driver adapted from the libopencm3 USB CDC ACM, USART, and timer 
examples:
- https://github.com/libopencm3/libopencm3-examples/tree/master/examples/stm32/f1/stm32-maple/usb_cdcacm
- https://github.com/libopencm3/libopencm3-examples/tree/master/examples/stm32/f1/stm32-maple/usart
- https://github.com/libopencm3/libopencm3-examples/blob/master/examples/stm32/f1/stm32-h103/timer

The SAE J1708 code is influenced by:
- https://github.com/freddy120/UARTJ1708_atmel

This code works with an STM32 "bluepill" (STM32F103C8T6) board wired to 
a copperhill SAE J1708 breakout board on USART1 (PA9 for Tx, PA10 for Rx):
- https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill.html
- https://copperhilltech.com/sae-j1708-to-uart-breakout-board

