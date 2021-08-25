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

# Required Tools
Because the firmware is built using the STM32 Arduino core there are many 
settings required to get it to build and flash correctly.  The following will be 
needed:
- arduino-cli or Arduino IDE
- Arduino_Core_STM32 support (https://github.com/stm32duino/Arduino_Core_STM32)
- dfu-util
- python 3.8+
- yq (required by the install_arduino_cli.sh script)

`arduino-cli` installation instructions can be found here: 
https://arduino.github.io/arduino-cli/latest/installation/.  This code was 
tested with version 1.9.0 of the Arduino_Core_STM32.  That can be installed by 
connecting the following board manager json file to the Arduino tools:
- https://github.com/stm32duino/BoardManagerFiles/raw/master/STM32/package_stm_index.json

NOTE: for the moment you must manually apply some fixes to the STM32 build
script and platform config: https://github.com/stm32duino/Arduino_Core_STM32/pull/1442

The `arduino-cli` and necessary boards can be installed and configured 
automatically with the `install_arduino_cli.sh` script.  This script installs 
`arduino-cli` using `go`.  If you would prefer not to mess with go, install the 
latest `arduino-cli` using the instructions on that project's page and the 
`install_arduino_cli.sh` script will only install the STM32 board manager files.

## Compiling
The firmware can be built and installed by running the following commands in 
this or the `firmware/` directory.
```
$ make
$ make flash
```

## Bootloader

This board was programmed with the `generic_boot20_pc13.bin` Arduino compatible 
bootloader from the STM32duino project 
(https://github.com/rogerclarkmelbourne/STM32duino-bootloader/) with this 
command:
```
st-flash write bootloader_only_binaries/generic_boot20_pc13.bin 0x8000000
```

# About
The SAE J1708 code is influenced by:
- https://github.com/freddy120/UARTJ1708_atmel

This code works with an STM32 "bluepill" (STM32F103C8T6) board wired to 
a copperhill SAE J1708 breakout board on USART1 (PA9 for Tx, PA10 for Rx):
- https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill.html
- https://copperhilltech.com/sae-j1708-to-uart-breakout-board
