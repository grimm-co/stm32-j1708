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

An interactive python frontend is also available:
```
$ j1708.py -p <port>
```

A J1708 object called `j` is created and use to send and receive J1708 messages. More
usage information can be found by typing `j?` and hitting enter at the prompt.

# Required Tools
Because the firmware is built using the STM32 Arduino core there are many
settings required to get it to build and flash correctly.  The following will be
needed:
- arduino-cli or Arduino IDE
- Arduino_Core_STM32 support (https://github.com/stm32duino/Arduino_Core_STM32)
- dfu-util
- python 3.8+
- yq (required by the install_arduino_cli.sh script if you use it)

`arduino-cli` installation instructions can be found here:
https://arduino.github.io/arduino-cli/latest/installation/.  This code was
tested with version 2.0.0 of the Arduino_Core_STM32.  That can be installed by
connecting the following board manager json file to the Arduino tools:
- https://raw.githubusercontent.com/stm32duino/BoardManagerFiles/main/package_stmicroelectronics_index.json

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

By default the makefile will use the `arduino-cli` command line tool to build
the firmware `dfu-util` to flash a "bluepill" STM32F103C8T6 board.

## Supported Hardware
### STM32F103 "bluepill"
This tool was originally developed using a "bluepill" devboard.

When used with the "bluepill" board you first need to flash an Arduino
compatible booloader onto the board since the bluepill does not typically use
genuine STM32 processors and do not come with a DFU-compatible bootloader
pre-programmed.

#### Bootloader
This board was programmed with the `generic_boot20_pc13.bin` Arduino compatible
bootloader from the STM32duino project
(https://github.com/rogerclarkmelbourne/STM32duino-bootloader/) with this
command:
```
st-flash write bootloader_only_binaries/generic_boot20_pc13.bin 0x8000000
```

### STM32F411 "blackpill"
This tool has been tested with a "blackpill" STM32F411 devboard.  When targeting
the blackpill use the following commands to compile and flash the target board
(if using the makefile and command line `arduino-cli` tools):
```
make TARGET=BLACKPILL
make TARGET=BLACKPILL flash
```

The standard flash method configured in the `blackpill_sketch.json` is DFU using
`stm32CubeProg` dfu method. So you will need the STM32Cube tools installed
before this will work.

If using a blackpill board that is not the STM32F411 board available on Adafruit
the `sketch.json` file will need to be customized, or manually configured and
compiled through the normal Arduino IDE.

# About
The SAE J1708 code is influenced by:
- https://github.com/freddy120/UARTJ1708_atmel

This code works with an STM32 "bluepill" (STM32F103C8T6) board wired to
a copperhill SAE J1708 breakout board on USART1 (PA9 for Tx, PA10 for Rx):
- https://stm32world.com/wiki/Blue_Pill
- https://copperhilltech.com/sae-j1708-to-uart-breakout-board

This code is also tested on the "blackpill" (STM32F411) board with the same
connections to the J1708 breakout board:
- https://stm32world.com/wiki/Black_Pill
- https://www.adafruit.com/product/4877
