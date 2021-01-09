FQBN    := STM32:stm32:GenF1
PNUM    := BLUEPILL_F103C8
XSERIAL := none
USB     := CDCgen
XUSB    := FS
OPT     := o3lto
RTLIB   := nano

.PHONY: build

build:
	arduino-cli compile -b $(FQBN):pnum=$(PNUM),xserial=$(XSERIAL),usb=$(USB),xusb=$(XUSB),opt=$(OPT),rtlib=$(RTLIB)
