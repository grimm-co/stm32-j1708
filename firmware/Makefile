TARGET    ?= BLUEPILL
ifeq ($(TARGET),BLUEPILL)
	SKETCH_JSON := bluepill_sketch.json
else
ifeq ($(TARGET),BLACKPILL)
	SKETCH_JSON := blackpill_sketch.json
else
$(error Inavlid TARGET ($(TARGET)) choose one of BLUEPILL or BLACKPILL)
endif
endif

PROJECT   := $(notdir $(shell pwd))
BIN       := $(PROJECT).ino.bin
BUILD_DIR := build

SRC_FILES := $(PROJECT).ino $(wildcard *.cpp) $(wildcard *.h)

# Arduino tools like to agressively cache various build components but sometimes 
# these need to be rebuilt to deal with #define changes, or just for a clean 
# build.
SKETCH_CACHE := $(shell arduino-cli compile --show-properties 2> /dev/null | grep -oP "build.path=\K.*")

# Put the trailing '/' here so the remove command later doesn't accidentally 
# kill the root directory if something goes wrong with this variable
CORE_CACHE   := /tmp/arduino-core-cache/

# Programming settings
DFU_USB_ID  := 1EAF:0003
DFU_PROFILE := 2
APP_USB_ID  := 0483:5740
RESET_UTIL  := ../stm32duino-reset

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

# If custom commands are supplied to arduino-cli with the --build-property 
# argument the build.extra_flags must include these settings to work properly:
STM32_DEFAULT_CONIG := \
	-D{build.product_line} \
	{build.enable_usb} \
	{build.xSerial} \
	{build.bootloader_flags}

# Customize the target USB descriptions
STM32_USB_CONFIG := \
	\"-DUSB_MANUFACTURER_STRING=\"GRIMM\"\" \
	\"-DUSB_PRODUCT_STRING=\"J1708 Tool\"\"

# No additional project config settings necessary at this time
PROJECT_CONFIG :=

ARDUINO_CLI_ARGS := $(STM32_DEFAULT_CONIG) $(STM32_USB_CONFIG) $(PROJECT_CONFIG)

.PHONY: default verbose flash clean distclean

default: $(BUILD_DIR)/$(BIN)

verbose: VERBOSE := -v
verbose: default

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/$(BIN): $(SRC_FILES) $(SKETCH_JSON) | $(BUILD_DIR)
	cp $(SKETCH_JSON) sketch.json
	arduino-cli compile --build-property="build.extra_flags=$(ARDUINO_CLI_ARGS)" --output-dir=$(BUILD_DIR) $(VERBOSE)

flash: $(BUILD_DIR)/$(BIN)
ifeq ($(TARGET_MODE),APPLICATION)
	python $(RESET_UTIL) -d $(APP_USB_ID)
endif
	dfu-util -d $(DFU_USB_ID) -a $(DFU_PROFILE) -D $< -R

clean:
ifneq ($(wildcard $(BUILD_DIR)/*),)
	rm $(wildcard $(BUILD_DIR)/*)
endif

distclean: clean
ifneq ($(wildcard sketch.json),)
	rm -f sketch.json
endif
ifneq ($(SKETCH_CACHE),)
	rm -rf $(SKETCH_CACHE)
endif
ifneq ($(wildcard $(CORE_CACHE)*),)
	rm -rf $(wildcard $(CORE_CACHE)*)
endif

