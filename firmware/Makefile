
PROJECT   := $(notdir $(shell pwd))
BIN       := $(PROJECT).ino.bin
BUILD_DIR := build
SRC_FILES := $(PROJECT).ino sketch.json $(wildcard *.cpp) $(wildcard *.h)

# Programming settings
DFU_USB_ID  := 1EAF:0003
DFU_PROFILE := 2

APP_USB_ID  := 0483:5740

TARGET_MODE := $(shell lsusb -d 1EAF:0003 && echo "BOOTLOADER" || echo "APPLICATION")

# These settings aren't needed anymore since the sketch.json file has been 
# created, but keeping it here for now.
BOARD     := STM32:stm32:GenF1
PNUM      := BLUEPILL_F103C8
XSERIAL   := none
USB       := CDC
XUSB      := FS
OPT       := o2std
OPT_FLAGS := -O2
RTLIB     := nano
UPLOAD    := dfu2Method

FQBN      := $(BOARD):pnum=$(PNUM),xserial=$(XSERIAL),usb=$(USB),xusb=$(XUSB),opt=$(OPT),rtlib=$(RTLIB),upload_method=$(UPLOAD)

.PHONY: firmware flash clean

firmware: $(BUILD_DIR)/$(BIN)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/$(BIN): $(SRC_FILES) | $(BUILD_DIR)
	arduino-cli compile --output-dir=$(BUILD_DIR)

flash: $(BUILD_DIR)/$(BIN)
ifeq ($(TARGET_MODE),APPLICATION)
	python ../stm32duino-reset -d $(APP_USB_ID)
endif
	dfu-util -d $(DFU_USB_ID) -a $(DFU_PROFILE) -D $< -R

clean:
ifneq ($(wildcard $(BUILD_DIR)/*),)
	rm $(wildcard $(BUILD_DIR)/*)
endif
