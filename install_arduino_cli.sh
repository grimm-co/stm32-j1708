#!/bin/bash
set -o pipefail

# Is arduino-cli installed?
arduino-cli version > /dev/null 2>&1
if [ "$?" -ne 0 ]; then
    go get -u github.com/arduino/arduino-cli

    # Create a config
    arduino-cli config init

    # probably not necessary just after install but just in case - update the 
    # core and library indexes
    arduino-cli core update-index
    arduino-cli lib update-index

    # Install the arduino SAM cores first
    arduino-cli core install arduino:sam
fi

arduino-cli config dump | grep "stm32duino" > /dev/null 2>&1
if [ "$?" -ne 0 ]; then
    # Add the STM32 boards
    arduino-cli config add board_manager.additional_urls https://github.com/stm32duino/BoardManagerFiles/raw/master/STM32/package_stm_index.json

    # No need to update-index here since we will do it in the next step
fi

# Install the STM32 cores
arduino-cli board listall | grep "STM32:stm32:GenF1" > /dev/null 2>&1
if [ "$?" -ne 0 ]; then
    # Do an update just in case the arduino-cli wasn't installed this run and it 
    # needs updated
    arduino-cli core update-index
    arduino-cli core install STM32:stm32

    # Just in case there are any libraries required by the STM32 boards?
    arduino-cli lib update-index
    arduino-cli lib upgrade
else
    # Everything should be installed, just do an update of what is already 
    # installed
    arduino-cli core update-index
    arduino-cli core upgrade
    arduino-cli lib update-index
    arduino-cli lib upgrade
fi
