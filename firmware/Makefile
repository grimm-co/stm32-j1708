# Makefile for stm32-j1708

###############################################################################

PROJECT := stm32-j1708
DEVICE  := stm32f103x8
SRC     := $(wildcard *.c)
OBJS    := $(SRC:%.c=%.o)

ELF      := $(PROJECT).elf
BIN      := $(PROJECT).bin
HEX      := $(PROJECT).hex
MAP      := $(PROJECT).map
LIST     := $(PROJECT).list

OPENCM3_DIR := libopencm3

# Defines all the standard gcc executables (defined above)
include $(OPENCM3_DIR)/mk/gcc-config.mk

#PREFIX   ?= arm-none-eabi-
#CC       ?= $(PREFIX)gcc
#LD       ?= $(PREFIX)ld
#OBJCOPY  ?= $(PREFIX)objcopy
#OBJDUMP  ?= $(PREFIX)objdump
#SIZE     ?= $(PREFIX)size
#NM       ?= $(PREFIX)nm

LIBC     := $(shell $(CC) $(CFLAGS) --print-file-name=libc.a)
LIBGCC   := $(shell $(CC) $(CFLAGS) --print-libgcc-file-name)
LIBNOSYS := $(shell $(CC) $(CFLAGS) --print-file-name=libnosys.a)
LDLIBS   = -Wl,--start-group $(LIBC) $(LIBGCC) $(LIBNOSYS) -Wl,--end-group
LDFLAGS  = -static -nostartfiles
CPPFLAGS = -MMD -MP
CFLAGS   = -O2 -std=gnu99 \
	-Wall -Wextra -Wimplicit-function-declaration \
	-Wredundant-decls -Wmissing-prototypes -Wstrict-prototypes \
	-Wundef -Wshadow -fno-common -Wstrict-prototypes \
	-ffunction-sections -fdata-sections

###############################################################################

.PHONY: build clean distclean flash size symbols opencm3

# Default build target
build: $(BIN) $(HEX) $(LIST) size

###############################################################################

# Defines all of the link script options and rules based on DEVICE
#include $(OPENCM3_DIR)/mk/genlink-config.mk

# I don't like using this because it requires building the libopencm3 library 
# first and then running make on the project.  This seems silly.
# Instead all of the appropriate output is defined here
LDSCRIPT   := generated.$(DEVICE).ld
CPPFLAGS   += -DSTM32F1 -DSTM32F103X8
ARCH_FLAGS := -march=armv7-m -mtune=cortex-m3 -mthumb -msoft-float -mfix-cortex-m3-ldrd
LIBNAME    := opencm3_stm32f1.a
#LDLIBS     += -l$(LIBNAME)
LDLIBS     += $(OPENCM3_DIR)/lib/lib$(LIBNAME)
LIBDEPS    += $(OPENCM3_DIR)/lib/lib$(LIBNAME)
LDFLAGS    += -L$(OPENCM3_DIR)/lib
CPPFLAGS   += -I$(OPENCM3_DIR)/include

# Defines all of the target specific compile options based on DEVICE
include $(OPENCM3_DIR)/mk/genlink-rules.mk

# Board-specific defs (now handled by the libopencm3/mk/genlink-config.mk file)
#ARCH_FLAGS = -DSTM32F1 -mthumb -march=cortex-m3 -msoft-float -mfix-cortex-m3-ldrd
#LDSCRIPT   = $(OPENCM3_DIR)/lib/stm32/f1/stm32f103x8.ld
#LIBOPENCM3 = $(OPENCM3_DIR)/lib/libopencm3_stm32f1.a

###############################################################################

LDPATH   = $(OPENCM3_DIR)/lib/
#LDFLAGS += -Wl,-T$(LDSCRIPT) -Wl,-Map=$(MAP) -Wl,--gc-sections -Wl,--print-gc-sections
LDFLAGS += -Wl,-T$(LDSCRIPT) -Wl,-Map=$(MAP) -Wl,--gc-sections

DEPS    := $(SRC:%c=%.d)

-include $(DEPS)

###############################################################################

opencm3: $(OPENCM3_DIR)/lib/lib$(LIBNAME).a
$(OPENCM3_DIR)/lib/lib$(LIBNAME).a:
	$(MAKE) -C $(OPENCM3_DIR) TARGETS=stm32/f1 V=1

# Standard compilation rules
#include $(OPENCM3_DIR)/mk/gcc-rules.mk

$(ELF): $(LIBDEPS) $(LDSCRIPT) $(OBJS)
	$(LD) $(OBJS) $(LDLIBS) $(LDFLAGS) $(ARCH_FLAGS) -o $@

$(LIST): $(ELF)
	$(OBJDUMP) -d $< > $@

%.hex: %.elf
	$(OBJCOPY) -S -O ihex   $< $@

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@

%.o: %.c
	$(CC) $(CFLAGS) $(CPPFLAGS) $(ARCH_FLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(LDSCRIPT) $(ELF) $(HEX) $(BIN) $(MAP) $(LIST)

distclean: clean
	rm -f $(DEPS)
	$(MAKE) -C $(OPENCM3_DIR) clean

flash: $(HEX)
	st-flash --reset --format ihex write $<

size: $(PROJECT).elf
	@echo ""
	@$(SIZE) $(PROJECT).elf
	@echo ""

symbols: $(ELF)
	@$(NM) --demangle --size-sort -S $< | grep -v ' [bB] '

debug: $(ELF) flash
	(st-util &); gdb-multiarch $< -ex "target remote localhost:4242"
